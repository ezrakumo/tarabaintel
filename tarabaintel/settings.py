import os
from pathlib import Path
import dj_database_url
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ 1. SECURE SECRET KEY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-key-for-local-dev-only-CHANGE-IN-PRODUCTION')

# ✅ 2. SECURE DEBUG
DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']

# ✅ 3. SECURE HOSTS (Cleaned up, no duplicates)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
for host in ['localhost', '127.0.0.1', 'tarabaintel-ai.onrender.com', '*']:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# ✅ 4. SECURE PROXY SETTINGS (Required for Render's HTTPS load balancer)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# ✅ 5. SECURE COOKIES
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ✅ 6. INSTALLED APPS
INSTALLED_APPS = [
    'jazzmin', # ✅ MUST BE FIRST!
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # For development
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django.contrib.gis',
    'corsheaders',
    'channels',
    
    # Your apps
    'accounts',
    'insight',
]

# ✅ 7. MIDDLEWARE (CorsMiddleware MUST be at the very top)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', 
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tarabaintel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tarabaintel.wsgi.application'
ASGI_APPLICATION = 'tarabaintel.asgi.application'

# ✅ 8. DATABASE CONFIGURATION (PostGIS)
db_url = os.environ.get('DATABASE_URL', 'postgresql://tarabaintel_user:7n2CKWXlQJrCYzlzoaVejxvoRW0sUPih@dpg-dae5d5dbedkc73bd8d20-a.oregon-postgres.render.com/tarabaintel')
is_sqlite = 'sqlite' in db_url

DATABASES = {
    'default': dj_database_url.config(
        default=db_url,
        conn_max_age=600,
        ssl_require=not is_sqlite
    )
}

if not is_sqlite:
    DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# ✅ 9. LOCAL WINDOWS POSTGIS PATHS (Ignored on Render/Linux)
if os.name == 'nt':
    os.environ['PATH'] = r'C:\Program Files\PostgreSQL\18\bin' + os.pathsep + os.environ.get('PATH', '')
    GDAL_LIBRARY_PATH = r'C:\Program Files\PostgreSQL\18\bin\libgdal-35.dll'
    GEOS_LIBRARY_PATH = r'C:\Program Files\PostgreSQL\18\bin\libgeos_c.dll'

# ✅ 10. PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ✅ 11. STATIC FILES (Fixed & Consolidated)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# ✅ ADD THIS LINE FOR GUNICORN STATIC FILE SERVING
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ 12. CORS SETTINGS (Cleaned up)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = ['accept', 'accept-encoding', 'authorization', 'content-type', 'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with']

# ✅ 13. REST FRAMEWORK & JWT SETTINGS
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# ✅ 14. EMAIL CONFIGURATION (Cleaned up, single source of truth)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'ezrakumo@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '#MYGMAIL1@.kure2#')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

WEEKLY_FORECAST_RECIPIENTS = os.environ.get(
    'WEEKLY_FORECAST_RECIPIENTS', 
    'admin@tarabaintel.gov.ng,ops@tarabaintel.gov.ng'
).split(',')

# ✅ 15. CHANNELS / WEBSOCKET SETTINGS (Properly closed!)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ==========================================
# ✅ JAZZMIN ADMIN THEME CONFIGURATION
# ==========================================
JAZZMIN_SETTINGS = {
    "site_title": "TarabaInsight Command",
    "site_header": "TarabaInsight Intelligence",
    "site_brand": "TarabaInsight",
    "welcome_sign": "Welcome to the National Security Intelligence Command Center",
    "copyright": "TarabaInsight AI - 2026",
    "search_model": ["auth.User", "insight.Report"],
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Live Map", "url": "https://tarabaintel-ai.onrender.com/api/predictive-hotspots/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["auth", "insight", "accounts"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user-shield",
        "auth.Group": "fas fa-users",
        "insight.Report": "fas fa-exclamation-triangle",
        "insight.FieldVerification": "fas fa-clipboard-check",
        "insight.IntelligenceSummary": "fas fa-brain",
        "insight.UserProfile": "fas fa-id-card",
        "accounts": "fas fa-address-book",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-danger",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-danger",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly", # ✅ DARK THEME FOR COMMAND CENTER VIBE
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
