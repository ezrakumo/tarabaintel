from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # ✅ DEFAULT ADMIN
    # ... rest of your URLs
    # ✅ 4. AUTH ROUTES
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_login_legacy'), # ✅ ADD THIS LINE!
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]