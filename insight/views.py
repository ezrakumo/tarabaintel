import os
import csv
import io
import requests
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Report, FieldAgent, FieldVerification, LGA, IntelligenceSummary, PatternAlert
from .serializers import (
    ReportSerializer, 
    FieldVerificationSerializer, 
    VerificationClaimSerializer, 
    VerificationCompleteSerializer
)
from insight.services.intelligence_service import IntelligenceGenerationService


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('-submitted_at')
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        # 1. Save the report as RAW first
        report = serializer.save(status='RAW')
        
        # 2. Send to AI Microservice (Now Cloud-Native!)
        try:
            # Get the AI URL from environment variables, fallback to local for testing
            ai_base_url = os.environ.get('AI_SERVICE_URL', 'http://127.0.0.1:8001')
            ai_url = f"{ai_base_url}/analyze"
            
            ai_payload = {
                "report_id": str(report.id),
                "description": report.description,
                "issue_category": report.issue_category
            }
            
            # Increased timeout to 15s to account for cloud server wake-up time
            response = requests.post(ai_url, json=ai_payload, timeout=15)
            
            if response.status_code == 200:
                ai_data = response.json()
                
                report.ai_suggested_category = ai_data.get('ai_suggested_category', '')
                report.ai_confidence_score = float(ai_data.get('ai_confidence_score', 0.0))
                report.ai_sentiment = ai_data.get('sentiment', '')
                report.ai_urgency_level = ai_data.get('urgency_level', '')
                report.ai_extracted_entities = ai_data.get('extracted_entities', {})
                
                report.save()
                print(f"✅ AI Analysis successful for Report {report.id}")
                
                # AUTO-ASSIGNMENT & EMAIL ALERT: If AI flagged as CRITICAL
                if ai_data.get('urgency_level') == 'CRITICAL':
                    FieldVerification.objects.create(
                        report=report,
                        status='PENDING'
                    )
                    print(f"🚨 CRITICAL report detected! Auto-created verification task for Report {report.id}")
                    
                    # --- NEW: SEND FLASH EMAIL ALERT ---
                    try:
                        lga_name = report.lga.name if report.lga else 'Unknown'
                        subject = f"🚨 CRITICAL THREAT ALERT: {report.issue_category} in {lga_name}"
                        message = f"""
URGENT INTELLIGENCE ALERT

A CRITICAL threat has been reported and verified by AI.

Description: {report.description}
Location: {lga_name}
AI Confidence: {report.ai_confidence_score}%
Time: {report.submitted_at}

Login to the Command Center immediately to review.
"""
                        # Send to the command center (REPLACE WITH REAL EMAILS)
                        send_mail(
                            subject, 
                            message, 
                            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@tarabaintel.com'), 
                            ['admin@tarabaintel.gov.ng', 'ops@tarabaintel.gov.ng'], # <-- UPDATE THESE EMAILS
                            fail_silently=True, # True prevents app crash if email isn't configured yet
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
        """Export all reports to a CSV file for offline analysis"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tarabaintel_intelligence_export.csv"'

        writer = csv.writer(response)
        # Write the header row
        writer.writerow([
            'Report ID', 'Submitted At', 'LGA', 'Category', 
            'Urgency Level', 'AI Confidence', 'Description', 'Status'
        ])

        # Write the data rows
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


def intelligence_dashboard(request):
    """Real-time intelligence dashboard view - Bulletproof Version"""
    reports = Report.objects.all().order_by('-submitted_at')[:50]
    
    stats = {
        'total_reports': Report.objects.count(),
        'critical_count': Report.objects.filter(ai_urgency_level='CRITICAL').count(),
        'high_count': Report.objects.filter(ai_urgency_level='HIGH').count(),
        'verified_count': Report.objects.filter(status='VERIFIED').count(),
    }
    
    map_data = []
    for report in reports:
        if report.location:
            try:
                coords = report.location.coords
                lga_name = report.lga.name if report.lga else 'Unknown'
                
                map_data.append({
                    'id': str(report.id),
                    'lng': float(coords[0]),
                    'lat': float(coords[1]),
                    'description': report.description[:150] if report.description else 'No description',
                    'category': report.ai_suggested_category or report.issue_category or 'General',
                    'urgency': report.ai_urgency_level or 'MEDIUM',
                    'confidence': round(report.ai_confidence_score * 100, 1) if report.ai_confidence_score else 0.0,
                    'lga': lga_name,
                    'submitted': report.submitted_at.strftime('%b %d, %Y %H:%M') if report.submitted_at else 'Unknown',
                    'image_base64': report.image_base64 or '',
                })
            except Exception:
                continue 
            
    context = {
        'stats': stats,
        'map_data': map_data,
        'reports': reports,
    }
    
    return render(request, 'dashboard_v2.html', context)


@api_view(['GET'])
def test_ai_engine(request):
    """
    Temporary endpoint to test the AI Intelligence Analyzer in production.
    NOTE: In final production, this should be protected with @permission_classes([IsAdminUser]) 
    or removed entirely in favor of automated background tasks (Celery).
    """
    try:
        service = IntelligenceGenerationService()
        summary = service.generate_daily_sitrep()
        service.check_for_alerts()
        
        if summary:
            return Response({
                "status": "SUCCESS",
                "message": "AI Engine executed successfully!",
                "summary": {
                    "title": summary.title,
                    "briefing": summary.executive_briefing,
                    "findings": summary.key_findings,
                    "stats": summary.statistics
                }
            })
        else:
            return Response({
                "status": "NO_DATA",
                "message": "No reports found in the last 24 hours to analyze. Try submitting a new report first!"
            })
    except Exception as e:
        return Response({"status": "ERROR", "message": str(e)}, status=500)
        

def intelligence_briefing_dashboard(request):
    """Executive Intelligence Dashboard for Stakeholders"""
    latest_summary = IntelligenceSummary.objects.first()
    recent_alerts = PatternAlert.objects.filter(acknowledged=False).order_by('-detected_at')[:5]
    
    summaries_history = IntelligenceSummary.objects.order_by('generated_at')[:7]
    
    chart_labels = []
    chart_volumes = []
    chart_critical = []
    
    for summary in summaries_history:
        chart_labels.append(summary.generated_at.strftime('%b %d'))
        chart_volumes.append(summary.statistics.get('total_reports', 0))
        chart_critical.append(summary.statistics.get('critical_incidents', 0))
        
    context = {
        'latest_summary': latest_summary,
        'recent_alerts': recent_alerts,
        'chart_labels': chart_labels,
        'chart_volumes': chart_volumes,
        'chart_critical': chart_critical,
    }
    
    return render(request, 'intelligence_dashboard.html', context)