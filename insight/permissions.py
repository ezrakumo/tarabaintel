from rest_framework import permissions
from .models import UserProfile

# Define hierarchy levels for our RBAC
TIER_LEVELS = {
    'CITIZEN': 0,
    'VOLUNTEER': 1,
    'INFORMANT': 2,
    'AGENT': 3,
}

class IsCitizenOrAbove(permissions.BasePermission):
    """Allows access to all authenticated users with at least a CITIZEN tier."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            profile = request.user.intel_profile
            return TIER_LEVELS.get(profile.tier, 0) >= TIER_LEVELS['CITIZEN']
        except UserProfile.DoesNotExist:
            return False

class IsVolunteerOrAbove(permissions.BasePermission):
    """Allows access to users with at least a VOLUNTEER tier."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            profile = request.user.intel_profile
            return TIER_LEVELS.get(profile.tier, 0) >= TIER_LEVELS['VOLUNTEER']
        except UserProfile.DoesNotExist:
            return False

class IsInformantOrAbove(permissions.BasePermission):
    """Allows access to users with at least an INFORMANT tier."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            profile = request.user.intel_profile
            return TIER_LEVELS.get(profile.tier, 0) >= TIER_LEVELS['INFORMANT']
        except UserProfile.DoesNotExist:
            return False

class IsAgentOnly(permissions.BasePermission):
    """Allows access ONLY to users with the AGENT tier."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            profile = request.user.intel_profile
            return profile.tier == 'AGENT'
        except UserProfile.DoesNotExist:
            return False