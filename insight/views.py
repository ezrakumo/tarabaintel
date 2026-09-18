import os
import csv
import json
import requests
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Count, Q
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.contrib.gis.geos import Point

from .models import (
    Report, FieldAgent, FieldVerification, LGA, 
    IntelligenceSummary, PatternAlert, RewardCatalog, 
    RewardLedger, UserProfile
)
from .serializers import (
    ReportSerializer, 
    FieldVerificationSerializer, 
    VerificationClaimSerializer, 
    VerificationCompleteSerializer,
    RedeemRewardSerializer
)
from insight.services.intelligence_service import IntelligenceGenerationService
from insight.services.quality_grader import grade_and_reward_report

# ✅ WebSocket Imports
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# ✅ Predictive AI Import
from .services.hotspot_predictor import HotspotPredictor


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('-submitted_at')
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        print(f"📝 Starting report creation for user: {self.request.user}")
        
        # 1. Save the report as RAW first
        report = serializer.save(status='RAW', submitted_by=self.request.user)
        print(f"💾 Report {report.id} saved to database successfully.")
        
        # 2. ✅ SMART COORDINATE FALLBACK
        lga_coords = {
            'Jalingo': (8.8833, 11.3667),
            'Wukari': (7.8714, 9.7833),
            'Gembu': (6.7333, 11.2667),
            'Bali': (7.8667, 10.9833),
            'Takum': (7.2333, 10.4167),
            'Ibi': (7.4833, 9.7500),
            'Sardauna': (7.0833, 11.5833),
            'Karim Lamido': (9.4833, 11.1167),
        }
        
        lat, lon = 8.8833, 11.3667  # Default to Jalingo
        
        print(f"🔍 DEBUG: Report LGA name from DB is: '{report.lga.name if report.lga else 'None'}'")

        if report.location:
            try:
                coords = report.location.wkt.replace('POINT (', '').replace(')', '').split(' ')
                lon, lat = float(coords[0]), float(coords[1])
            except Exception:
                pass
        elif report.lga and report.lga.name in lga_coords:
            lat, lon = lga_coords[report.lga.name]
            print(f"📍 Using LGA fallback coordinates for {report.lga.name}: {lat}, {lon}")
            
            report.location = Point(lon, lat)
            report.save(update_fields=['location'])
            print(f"💾 Saved fallback location to database for Report {report.id}")
        else:
            print(f"⚠️ WARNING: LGA '{report.lga.name}' not found in fallback dictionary!")

        # 3. ✅ BROADCAST TO REAL-TIME DASHBOARD IMMEDIATELY
        channel_layer = get_channel_layer()
        print(f"📡 Attempting to broadcast Report {report.id} to WebSocket...")
        try:
            async_to_sync(channel_layer.group_send)(
                'intelligence_feed',
                {
                    'type': 'new_threat',
                    'report': {
                        'id': str(report.id),
                        'category': report.issue_category or 'UNKNOWN',
                        'urgency': 'MODERATE',
                        'description': report.description,
                        'lat': lat,
                        'lon': lon
                    }
                }
            )
            print(f"✅ WebSocket broadcast SUCCESSFUL for Report {report.id}")
        except Exception as ws_error:
            print(f"❌ WebSocket broadcast FAILED: {ws_error}")

        # 4. Send to AI Microservice
        try:
            ai_base_url = os.environ.get('AI_SERVICE_URL', 'http://127.0.0.1:8001')
            ai_url = f"{ai_base_url}/analyze"
            
            ai_payload = {
                "report_id": str(report.id),
                "description": report.description,
                "issue_category": report.issue_category,
                "image_base64": report.image_base64,
            }
            
            response = requests.post(ai_url, json=ai_payload, timeout=45)
            
            if response.status_code == 200:
                ai_data = response.json()
                report.ai_suggested_category = ai_data.get('ai_suggested_category', '')
                report.ai_confidence_score = float(ai_data.get('ai_confidence_score', 0.0))
                report.ai_sentiment = ai_data.get('sentiment', '')
                report.ai_urgency_level = ai_data.get('urgency_level', '')
                report.ai_extracted_entities = ai_data.get('extracted_entities', {})
                report.save()
                print(f"✅ AI Analysis successful for Report {report.id}")
                
                # --- GRADE INTEL QUALITY AND AWARD POINTS ---
                try:
                    score, pts = grade_and_reward_report(report)
                    print(f"🏆 Intel Graded: Score {score}/100, Awarded {pts} points.")
                except Exception as grading_error:
                    print(f"⚠️ Grading/Reward system failed: {grading_error}")

                # AUTO-ASSIGNMENT & EMAIL ALERT: If AI flagged as CRITICAL
                if ai_data.get('urgency_level') == 'CRITICAL':
                    FieldVerification.objects.create(report=report, status='PENDING')
                    print(f"🚨 CRITICAL report detected! Auto-created verification task for Report {report.id}")
                    
                    try:
                        lga_name = report.lga.name if report.lga else 'Unknown'
                        subject = f"🚨 CRITICAL THREAT ALERT: {report.issue_category} in {lga_name}"
                        message = f"URGENT INTELLIGENCE ALERT\n\nA CRITICAL threat has been reported.\nDescription: {report.description}\nLocation: {lga_name}\nAI Confidence: {report.ai_confidence_score}%\nTime: {report.submitted_at}\n\nLogin to the Command Center immediately to review."
                        send_mail(
                            subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@tarabaintel.com'), 
                            ['admin@tarabaintel.gov.ng', 'ops@tarabaintel.gov.ng'], fail_silently=True
                        )
                        print("✅ Flash email alert queued/sent successfully.")
                    except Exception as email_error:
                        print(f"⚠️ Failed to send flash email: {email_error}")
            else:
                print(f"⚠️ AI Service returned status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ AI Service unavailable or crashed: {e}")

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tarabaintel_intelligence_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['Report ID', 'Submitted At', 'LGA', 'Category', 'Urgency Level', 'AI Confidence', 'Description', 'Status'])

        reports = Report.objects.all().order_by('-submitted_at')
        for report in reports:
            writer.writerow([
                str(report.id),
                report.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if report.submitted_at else '',
                report.lga.name if report.lga else 'Unknown',
                report.issue_category,
                report.ai_urgency_level or 'PENDING',
                f"{report.ai_confidence_score * 100:.1f}%" if report.ai_confidence_score else '0%',
                report.description,
                report.status
            ])
        return response


class FieldVerificationViewSet(viewsets.ModelViewSet):
    queryset = FieldVerification.objects.all().order_by('-assigned_at')
    serializer_class = FieldVerificationSerializer
    
    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        verification = self.get_object()
        serializer = VerificationClaimSerializer(data=request.data)
        
        if serializer.is_valid():
            agent_id = serializer.validated_data['agent_id']
            try:
                agent = FieldAgent.objects.get(agent_id=agent_id, is_active=True)
                if verification.status not in ['PENDING', 'ASSIGNED']:
                    return Response({'error': 'Already claimed or completed'}, status=status.HTTP_400_BAD_REQUEST)
                
                verification.assigned_agent = agent
                verification.status = 'IN_PROGRESS'
                verification.claimed_at = timezone.now()
                verification.save()
                verification.report.status = 'PENDING_VERIFICATION'
                verification.report.save()
                return Response({'message': f'Claimed by {agent.agent_id}'})
            except FieldAgent.DoesNotExist:
                return Response({'error': 'Invalid agent'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        verification = self.get_object()
        serializer = VerificationCompleteSerializer(data=request.data)
        
        if serializer.is_valid():
            agent_id = serializer.validated_data['agent_id']
            is_valid = serializer.validated_data['is_valid']
            notes = serializer.validated_data.get('notes', '')
            
            if verification.assigned_agent and verification.assigned_agent.agent_id != agent_id:
                return Response({'error': 'Only assigned agent can complete'}, status=status.HTTP_403_FORBIDDEN)
            
            verification.complete_verification(is_valid, notes)
            return Response({'message': 'Verification completed'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@staff_member_required
def intelligence_briefing_dashboard(request):
    latest_summary = IntelligenceSummary.objects.first()
    recent_alerts = PatternAlert.objects.filter(acknowledged=False).order_by('-detected_at')[:5]
    summaries_history = IntelligenceSummary.objects.order_by('-generated_at')[:7]
    
    chart_labels = []
    chart_volumes = []
    chart_critical = []
    
    for summary in reversed(summaries_history):
        chart_labels.append(summary.generated_at.strftime('%b %d'))
        stats = summary.statistics or {}
        chart_volumes.append(stats.get('total_reports', 0))
        chart_critical.append(stats.get('critical_incidents', 0))
        
    if latest_summary and latest_summary.statistics:
        stats = latest_summary.statistics
        total_reports = stats.get('total_reports', 0)
        critical_incidents = stats.get('critical_incidents', 0)
        hotspots_identified = stats.get('hotspots_identified', 0)
        trend = stats.get('trend', 'STABLE')
    else:
        total_reports = Report.objects.count()
        critical_incidents = Report.objects.filter(ai_urgency_level='CRITICAL').count()
        hotspots_identified = 0
        trend = 'STABLE'

    context = {
        'latest_summary': latest_summary, 
        'recent_alerts': recent_alerts,
        'chart_labels': json.dumps(chart_labels), 
        'chart_volumes': json.dumps(chart_volumes), 
        'chart_critical': json.dumps(chart_critical),
        'total_reports': total_reports, 
        'critical_incidents': critical_incidents,
        'hotspots_identified': hotspots_identified, 
        'trend': trend,
    }
    
    return render(request, 'intelligence_dashboard.html', context)


@api_view(['GET'])
def test_ai_engine(request):
    secret_token = request.GET.get('token', '')
    expected_token = os.environ.get('AI_CRON_SECRET', 'super_secret_default_token_123')
    
    if secret_token != expected_token:
        return Response({"status": "UNAUTHORIZED", "message": "Invalid secret token"}, status=403)

    try:
        service = IntelligenceGenerationService()
        summary = service.generate_daily_sitrep()
        service.check_for_alerts()
        
        if summary:
            return Response({
                "status": "SUCCESS", "message": "AI Engine executed successfully!",
                "summary": {
                    "title": summary.title, 
                    "briefing": summary.executive_briefing, 
                    "findings": summary.key_findings, 
                    "stats": summary.statistics
                }
            })
        else:
            return Response({"status": "NO_DATA", "message": "No reports found in the last 24 hours to analyze."})
    except Exception as e:
        return Response({"status": "ERROR", "message": str(e)}, status=500)
    

def rewards_dashboard_page(request):
    return render(request, 'rewards_dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rewards_dashboard_api(request):
    """API endpoint for the Flutter rewards dashboard"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        
        available_rewards = RewardCatalog.objects.filter(
            is_active=True,
            points_required__lte=profile.total_points
        ).values('id', 'title', 'points_required')
        
        return Response({
            'status': 'success',
            'user_tier': profile.tier,
            'total_points': profile.total_points,
            'available_rewards': list(available_rewards)
        })
    except UserProfile.DoesNotExist:
        return Response({'status': 'error', 'message': 'User profile not found'}, status=404)
    except Exception as e:
        print(f"❌ Rewards dashboard API error: {e}")
        return Response({'status': 'error', 'message': str(e)}, status=500)


class RedeemRewardView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = RedeemRewardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reward = serializer.validated_data['reward_id']
        
        profile = UserProfile.objects.select_for_update().get(user=request.user)

        if profile.total_points < reward.points_required:
            return Response({"error": "Insufficient points."}, status=status.HTTP_400_BAD_REQUEST)

        profile.total_points -= reward.points_required
        profile.save()

        RewardLedger.objects.create(
            user_profile=profile,
            transaction_type='REDEMPTION',
            points=-reward.points_required,
            description=f"Redeemed reward: {reward.title}"
        )

        return Response({
            "message": f"Successfully redeemed {reward.title}!",
            "new_balance": profile.total_points
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def predictive_hotspots(request):
    days = int(request.GET.get('days', 30))
    
    try:
        predictor = HotspotPredictor(eps=0.02, min_samples=2) 
        hotspots = predictor.generate_hotspots(days=days)
        
        return Response({
            'status': 'success',
            'days_analyzed': days,
            'hotspot_count': len(hotspots),
            'hotspots': hotspots
        })
    
    except Exception as e:
        print(f"❌ Predictive analytics failed: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_rewards(request):
    """Debug endpoint to see raw reward data"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    all_rewards = RewardCatalog.objects.filter(is_active=True)
    
    tier_order = ['CITIZEN', 'VOLUNTEER', 'INFORMANT', 'AGENT']
    try:
        user_tier_idx = tier_order.index(user_profile.tier)
    except ValueError:
        user_tier_idx = 0
        
    available_tiers = tier_order[:user_tier_idx + 1]
    
    filtered_rewards = RewardCatalog.objects.filter(
        is_active=True,
        min_tier_required__in=available_tiers,
        points_required__lte=user_profile.total_points
    )
    
    return Response({
        "user_tier": user_profile.tier,
        "user_points": user_profile.total_points,
        "available_tiers": available_tiers,
        "total_active_rewards": all_rewards.count(),
        "total_filtered_rewards": filtered_rewards.count(),
        "all_rewards": [
            {"title": r.title, "points": r.points_required, "tier_in_db": r.min_tier_required, "is_active": r.is_active}
            for r in all_rewards
        ],
        "filtered_rewards": [
            {"title": r.title, "points": r.points_required, "tier": r.min_tier_required}
            for r in filtered_rewards
        ]
    })
