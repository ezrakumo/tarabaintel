from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'is_agent': user.username.startswith('agent_')
        })
