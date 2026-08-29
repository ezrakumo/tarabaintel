import os
import requests
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Report, FieldAgent, FieldVerification
from .serializers import (
    ReportSerializer, 
    FieldVerificationSerializer, 
    VerificationClaimSerializer, 
    VerificationCompleteSerializer
)

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
            
            # Increased timeout to 15s to account for cloud server wake-up time (Render free tier)
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
                
                # AUTO-ASSIGNMENT: If AI flagged as CRITICAL, create verification task
                if ai_data.get('urgency_level') == 'CRITICAL':
                    FieldVerification.objects.create(
                        report=report,
                        status='PENDING'
                    )
                    print(f"🚨 CRITICAL report detected! Auto-created verification task for Report {report.id}")
            else:
                print(f"⚠️ AI Service returned status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ AI Service unavailable or crashed: {e}")