from rest_framework import serializers
from django.contrib.gis.geos import Point, GEOSGeometry
from .models import Report, FieldAgent, FieldVerification

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        
        read_only_fields = ['ai_suggested_category', 'ai_confidence_score', 
                           'ai_sentiment', 'ai_urgency_level', 'ai_extracted_entities']

    # --- THIS IS THE MAGIC FIX ---
    def create(self, validated_data):
        location_data = validated_data.pop('location', None)
        
        if location_data:
            # If the API sends a dictionary (GeoJSON)
            if isinstance(location_data, dict):
                coords = location_data.get('coordinates')
                validated_data['location'] = Point(coords[0], coords[1], srid=4326)
            # If the API sends a string (WKT)
            elif isinstance(location_data, str):
                validated_data['location'] = GEOSGeometry(location_data, srid=4326)
                
        return Report.objects.create(**validated_data)

class FieldAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldAgent
        fields = ['id', 'agent_id', 'phone_number', 'assigned_lgas', 'is_active']

class FieldVerificationSerializer(serializers.ModelSerializer):
    report = ReportSerializer(read_only=True)
    assigned_agent = FieldAgentSerializer(read_only=True)
    
    class Meta:
        model = FieldVerification
        fields = [
            'id', 'report', 'assigned_agent', 'verification_notes', 
            'verification_photos', 'is_verified', 'verified_at', 
            'assigned_at', 'claimed_at', 'completed_at', 'status'
        ]
        read_only_fields = ['id', 'assigned_at', 'claimed_at', 'completed_at', 'verified_at']

class VerificationClaimSerializer(serializers.Serializer):
    agent_id = serializers.CharField(max_length=50)

class VerificationCompleteSerializer(serializers.Serializer):
    agent_id = serializers.CharField(max_length=50)
    is_valid = serializers.BooleanField()
    notes = serializers.CharField(required=False, allow_blank=True)