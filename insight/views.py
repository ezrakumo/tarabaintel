import os
import csv
import json
import requests
import traceback
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
        print(f" Starting report creation for user: {self.request.user}")
        
        report = serializer.save(status='RAW', submitted_by=self.request.user)
        print(f"💾 Report {report.id} saved to database successfully.")
        
        lga_coords = {
            'Jalingo': (8.8833, 11.3667), 'Wukari': (7.8714, 9.7833),
            'Gembu': (6.7333, 11.2667), 'Bali': (7.8667, 10.9833),
            'Takum': (7.2333, 10.4167), 'Ibi': (7.4833, 9.7500),
            'Sardauna': (7.0833, 11.5833), 'Karim Lamido': (9.4833, 11.1167),
        }
        
        lat, lon = 8.8833, 11.3667
        
        if report.location:
            try:
                coords = report.location.wkt.replace('POINT (', '').replace(')', '').split(' ')
                lon, lat = float(coords[0]), float(coords[1])
            except Exception:
                pass
        elif report.lga and report.lga.name in lga_coords:
            lat, lon = lga_coords[report.lga.name]
            report.location = Point(lon, lat)
            report.save(update_fields=['location'])

        channel_layer = get_channel_layer()
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
                        'lat': lat, 'lon': lon
                    }
                }
            )
        except Exception as ws_error:
            print(f"❌ WebSocket broadcast FAILED: {ws_error}")

        # ✅ AI SERVICE CALL WITH GRACEFUL FALLBACK
        try:
            ai_base_url = os.environ.get('AI_SERVICE_URL', 'http://127.0.0.1:8001')
            response = requests.post(f"{ai_base_url}/analyze", json={
                "report_id": str(report.id), 
                "description": report.description,
                "issue_category": report.issue_category, 
                "image_base64": report.image_base64,
            }, timeout=15)
            
            if response.status_code == 200:
                ai_data = response.json()
                report.ai_suggested_category = ai_data.get('ai_suggested_category', '')
                report.ai_confidence_score = float(ai_data.get('ai_confidence_score', 0.0))
                report.ai_sentiment = ai_data.get('sentiment', '')
                report.ai_urgency_level = ai_data.get('urgency_level', 'MODERATE')
                report.ai_extracted_entities = ai_data.get('extracted_entities', {})
                report.status = 'PROCESSED'
                report.save()
            else:
                raise Exception("AI returned non-200 status")

        except Exception as e:
            print(f"⚠️ AI Service unavailable ({e}). Applying default grading.")
            report.ai_urgency_level = 'MODERATE'
            report.ai_confidence_score = 0.5
            report.status = 'PROCESSED'
            report.save()

        # ✅ GRADING & REWARDS (Runs even if AI fails)
        try:
            grade_and_reward_report(report)
            print(f"✅ Rewards processed for report {report.id}")
        except Exception as grade_error:
            print(f"❌ Grading failed: {grade_error}")
            try:
                profile = UserProfile.objects.get(user=report.submitted_by)
                profile.total_points += 1
                profile.save()
            except Exception:
                pass

        # ✅ CREATE VERIFICATION TASK FOR HIGH URGENCY
        if report.ai_urgency_level in ['CRITICAL', 'HIGH']:
            FieldVerification.objects.create(report=report, status='PENDING')

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tarabaintel_intelligence_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['Report ID', 'Submitted At', 'LGA', 'Category', 'Urgency Level', 'AI Confidence', 'Description', 'Status'])
        for report in Report.objects.all().order_by('-submitted_at'):
            writer.writerow([
                str(report.id), report.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if report.submitted_at else '',
                report.lga.name if report.lga else 'Unknown', report.issue_category,
                report.ai_urgency_level or 'PENDING', f"{report.ai_confidence_score * 100:.1f}%" if report.ai_confidence_score else '0%',
                report.description, report.status
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
                verification.assigned_agent = agent
                verification.status = 'IN_PROGRESS'
                verification.claimed_at = timezone.now()
                verification.save()
                verification.report.status = 'PENDING_VERIFICATION'
                verification.report.save()
                return Response({'message': f'Claimed by {agent.agent_id}'})
            except FieldAgent.DoesNotExist:
                all_agents = list(FieldAgent.objects.values_list('agent_id', flat=True))
                active_agents = list(FieldAgent.objects.filter(is_active=True).values_list('agent_id', flat=True))
                return Response({
                    'error': 'Invalid agent',
                    'debug_info': {
                        'you_sent': agent_id,
                        'all_agents_in_db': all_agents,
                        'active_agents_in_db': active_agents
                    }
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        verification = self.get_object()
        serializer = VerificationCompleteSerializer(data=request.data)
        if serializer.is_valid():
            agent_id = serializer.validated_data.get('agent_id')
            is_valid = serializer.validated_data['is_valid']
            notes = serializer.validated_data.get('notes', '')
            
            if agent_id and verification.assigned_agent and verification.assigned_agent.agent_id != agent_id:
                return Response({'error': 'Only the assigned agent can complete this task'}, status=status.HTTP_403_FORBIDDEN)
            
            verification.status = 'COMPLETED'
            if hasattr(verification, 'notes'):
                verification.notes = notes
            if hasattr(verification, 'is_valid'):
                verification.is_valid = is_valid
            verification.save()
            
            if verification.report:
                verification.report.status = 'VERIFIED' if is_valid else 'INVALID'
                verification.report.save()
                
            return Response({'message': 'Verification completed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@staff_member_required
def intelligence_briefing_dashboard(request):
    latest_summary = IntelligenceSummary.objects.first()
    recent_alerts = PatternAlert.objects.filter(acknowledged=False).order_by('-detected_at')[:5]
    summaries_history = IntelligenceSummary.objects.order_by('-generated_at')[:7]
    
    chart_labels, chart_volumes, chart_critical = [], [], []
    for summary in reversed(summaries_history):
        chart_labels.append(summary.generated_at.strftime('%b %d'))
        stats = summary.statistics or {}
        chart_volumes.append(stats.get('total_reports', 0))
        chart_critical.append(stats.get('critical_incidents', 0))
        
    stats = latest_summary.statistics if latest_summary else {}
    context = {
        'latest_summary': latest_summary, 'recent_alerts': recent_alerts,
        'chart_labels': json.dumps(chart_labels), 'chart_volumes': json.dumps(chart_volumes), 
        'chart_critical': json.dumps(chart_critical),
        'total_reports': stats.get('total_reports', Report.objects.count()), 
        'critical_incidents': stats.get('critical_incidents', Report.objects.filter(ai_urgency_level='CRITICAL').count()),
        'hotspots_identified': stats.get('hotspots_identified', 0), 
        'trend': stats.get('trend', 'STABLE'),
    }
    return render(request, 'intelligence_dashboard.html', context)


@api_view(['GET'])
def test_ai_engine(request):
    secret_token = request.GET.get('token', '')
    expected_token = os.environ.get('AI_CRON_SECRET', 'super_secret_default_token_123')
    if secret_token != expected_token:
        return Response({"status": "UNAUTHORIZED"}, status=403)
    try:
        service = IntelligenceGenerationService()
        summary = service.generate_daily_sitrep()
        service.check_for_alerts()
        return Response({"status": "SUCCESS", "summary": summary.title if summary else "No Data"})
    except Exception as e:
        return Response({"status": "ERROR", "message": str(e)}, status=500)
    

def rewards_dashboard_page(request):
    return render(request, 'rewards_dashboard.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rewards_dashboard_api(request):
    try:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'total_points': 0, 'lifetime_points': 0, 'tier': 'CITIZEN'}
        )
        
        print(f"🔍 Dashboard API called for user: {request.user.username}")
        print(f"📊 Profile total_points: {profile.total_points}")
        
        available_rewards = RewardCatalog.objects.filter(
            is_active=True, 
            points_required__lte=profile.total_points
        )
        
        recent_tx = RewardLedger.objects.filter(
            user_profile=profile
        ).order_by('-created_at')[:10]
        
        tier_order = ['CITIZEN', 'VOLUNTEER', 'INFORMANT', 'AGENT']
        current_idx = tier_order.index(profile.tier) if profile.tier in tier_order else 0
        next_tier = tier_order[current_idx + 1] if current_idx < len(tier_order) - 1 else None
        points_to_next = (current_idx + 1) * 100 - profile.total_points if next_tier else 0
        
        # ✅ USE CAMELCASE TO MATCH FLUTTER MODEL
        return Response({
            'status': 'success',
            'userTier': profile.tier,
            'totalPoints': profile.total_points,
            'lifetimePoints': profile.lifetime_points,
            'affordableRewards': [
                {
                    'id': r.id,
                    'title': r.title,
                    'description': r.description or '',
                    'pointsRequired': r.points_required,
                }
                for r in available_rewards
            ],
            'recentTransactions': [
                {
                    'type': tx.transaction_type,
                    'points': tx.points,
                    'description': tx.description,
                    'date': tx.created_at.isoformat() if tx.created_at else None,
                }
                for tx in recent_tx
            ],
            'nextTier': next_tier,
            'pointsToNextTier': max(0, points_to_next),
        })
        
    except Exception as e:
        import traceback
        print(f"❌ DASHBOARD API ERROR: {e}")
        print(traceback.format_exc())
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
            user_profile=profile, transaction_type='REDEMPTION',
            points=-reward.points_required, description=f"Redeemed reward: {reward.title}"
        )
        return Response({"message": f"Successfully redeemed {reward.title}!", "new_balance": profile.total_points}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def predictive_hotspots(request):
    days = int(request.GET.get('days', 30))
    try:
        predictor = HotspotPredictor(eps=0.02, min_samples=2) 
        hotspots = predictor.generate_hotspots(days=days)
        return Response({
            'status': 'success', 'days_analyzed': days,
            'hotspot_count': len(hotspots), 'hotspots': hotspots
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['GET'])
def trigger_weekly_forecast(request):
    from django.core.management import call_command
    secret_token = request.GET.get('token', '')
    expected_token = os.environ.get('AI_CRON_SECRET', 'super_secret_default_token_123')
    if secret_token != expected_token:
        return Response({"status": "UNAUTHORIZED", "message": "Invalid secret token"}, status=403)
    try:
        call_command('generate_weekly_forecast')
        return Response({"status": "SUCCESS", "message": "Weekly forecast initiated."})
    except Exception as e:
        return Response({"status": "ERROR", "message": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_rewards(request):
    user_profile = UserProfile.objects.get(user=request.user)
    all_rewards = RewardCatalog.objects.filter(is_active=True)
    tier_order = ['CITIZEN', 'VOLUNTEER', 'INFORMANT', 'AGENT']
    try:
        user_tier_idx = tier_order.index(user_profile.tier)
    except ValueError:
        user_tier_idx = 0
    available_tiers = tier_order[:user_tier_idx + 1]
    filtered_rewards = RewardCatalog.objects.filter(
        is_active=True, min_tier_required__in=available_tiers,
        points_required__lte=user_profile.total_points
    )
    return Response({
        "user_tier": user_profile.tier, "user_points": user_profile.total_points,
        "available_tiers": available_tiers, "total_active_rewards": all_rewards.count(),
        "total_filtered_rewards": filtered_rewards.count(),
        "all_rewards": [{"title": r.title, "points": r.points_required, "tier_in_db": r.min_tier_required} for r in all_rewards],
        "filtered_rewards": [{"title": r.title, "points": r.points_required, "tier": r.min_tier_required} for r in filtered_rewards]
    })
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_performance_analytics(request):
    """
    Returns 7-day submission trend and category breakdown for the logged-in user.
    """
    try:
        # 1. Calculate 7-Day Trend
        today = timezone.now().date()
        trend_data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = Report.objects.filter(
                submitted_at__date=day, 
                submitted_by=request.user
            ).count()
            trend_data.append({'date': day.strftime('%b %d'), 'count': count})

        # 2. Calculate Category Breakdown
        categories = Report.objects.filter(
            submitted_by=request.user
        ).values('issue_category').annotate(total=Count('id')).order_by('-total')
        
        category_data = [
            {'category': item['issue_category'] or 'Unknown', 'count': item['total']} 
            for item in categories
        ]

        # 3. Aggregate Stats
        total_reports = Report.objects.filter(submitted_by=request.user).count()
        profile = UserProfile.objects.get(user=request.user)

        return Response({
            'status': 'success',
            'total_reports': total_reports,
            'total_points': profile.total_points,
            'trend': trend_data,
            'categories': category_data
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)
