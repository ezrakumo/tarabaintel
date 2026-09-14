from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.contrib.auth import get_user_model

from .serializers import RedeemRewardSerializer
from .models import RewardCatalog, RewardLedger

# NOTE: Change 'users' to 'accounts' if your Profile model is in the accounts app!
from users.models import Profile 

User = get_user_model()

class RedeemRewardView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic # Prevents double-spending (Race Conditions)
    def post(self, request):
        serializer = RedeemRewardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reward = serializer.validated_data['reward_id']
        
        # Lock the profile row to prevent race conditions
        try:
            profile = Profile.objects.select_for_update().get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"error": "User profile not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if profile.total_points < reward.points_required:
            return Response(
                {"error": "Insufficient points."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduct points
        profile.total_points -= reward.points_required
        profile.save()

        # Create a ledger entry using your exact model names
        RewardLedger.objects.create(
            user=request.user,
            reward=reward, 
            points=-reward.points_required, 
            description=f"Redeemed: {reward.title}",
            transaction_type='REDEMPTION' 
        )

        return Response({
            "message": f"Successfully redeemed {reward.title}!",
            "new_balance": profile.total_points
        }, status=status.HTTP_201_CREATED)