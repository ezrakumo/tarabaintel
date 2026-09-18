from django.contrib import admin
from django.urls import path, include

# ✅ EXPLICITLY IMPORT ALL THE VIEWS WE NEED
from insight.views import (
    intelligence_briefing_dashboard,
    test_ai_engine,
    rewards_dashboard_page,
    rewards_dashboard_api,
    predictive_hotspots,
    debug_rewards
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include any app-specific URL configurations (like insight.urls if it exists)
    path('api/', include('insight.urls')), 
    
    # ✅ DIRECT VIEW ROUTES (No 'views.' prefix needed because we imported them directly above)
    path('command-dashboard/', intelligence_briefing_dashboard, name='command-dashboard'),
    path('api/test-ai/', test_ai_engine, name='test-ai'),
    path('rewards/dashboard/web/', rewards_dashboard_page, name='rewards-dashboard-web'),
    
    # ✅ THE FIX: This is the exact endpoint your Flutter app is calling
    path('api/rewards/dashboard/', rewards_dashboard_api, name='rewards-dashboard-api'),
    
    path('api/predictive-hotspots/', predictive_hotspots, name='predictive-hotspots'),
    path('api/debug-rewards/', debug_rewards, name='debug-rewards'),
]
