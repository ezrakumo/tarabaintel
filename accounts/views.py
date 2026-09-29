from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from insight.models import UserProfile  # ✅ IMPORT UserProfile

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # ✅ GET OR CREATE THE USER PROFILE
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'total_points': 0, 'lifetime_points': 0, 'tier': 'CITIZEN'}
        )
        
        return Response({
            'username': user.username,
            'email': user.email,
            'is_agent': user.username.startswith('agent_'),
            'state': profile.state,  # ✅ NOW RETURNING THE STATE!
            'tier': profile.tier,
            'total_points': profile.total_points,
            'phone_number': profile.phone_number,
        })
        