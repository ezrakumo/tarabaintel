import os
from pathlib import Path
import dj_database_url
from datetime import timedelta

# ✅ 1. BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ 2. SECURITY SETTINGS
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-key-for-local-dev-only-CHANGE-IN-PRODUCTION')
DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']

# Clean and secure ALLOWED_HOSTS
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
ALLOWED_HOSTS.extend(['tarabaintel-ai.onrender.com', '*'])
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS)) # Remove duplicates

# Render HTTPS Proxy Settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ✅ 3. INSTALLED APPS
INSTALLED_APPS = [
    'jazzmin', # ✅ MUST BE BEFORE django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.gis', # ✅ For GeoDjango
    
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'django.contrib.gis',
    'corsheaders',
    'channels',
    
    # Local apps
    'accounts',
    'insight',
]

# ✅ 4. MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ MUST BE HERE
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

# ✅ 5. DATABASE CONFIGURATION (PostGIS)
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

# Local Windows PostGIS Paths (Ignored on Render/Linux)
if os.name == 'nt':
    os.environ['PATH'] = r'C:\Program Files\PostgreSQL\18\bin' + os.pathsep + os.environ.get('PATH', '')
    GDAL_LIBRARY_PATH = r'C:\Program Files\PostgreSQL\18\bin\libgdal-35.dll'
    GEOS_LIBRARY_PATH = r'C:\Program Files\PostgreSQL\18\bin\libgeos_c.dll'

# ✅ 6. PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ✅ 7. INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# ✅ 8. STATIC FILES (Modern Django 4.2+ Configuration)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ✅ This is the REQUIRED way to configure WhiteNoise in Django 4.2+
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# ✅ 9. CORS SETTINGS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = ['accept', 'accept-encoding', 'authorization', 'content-type', 'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with']

# ✅ 10. REST FRAMEWORK & JWT SETTINGS
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

# ✅ 11. EMAIL CONFIGURATION (SECURED)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'ezrakumo@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '') # ✅ SET IN RENDER ENV VARS
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

WEEKLY_FORECAST_RECIPIENTS = os.environ.get(
    'WEEKLY_FORECAST_RECIPIENTS', 
    'admin@tarabaintel.gov.ng,ops@tarabaintel.gov.ng'
).split(',')

# ✅ 12. CHANNELS / WEBSOCKET SETTINGS
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

   # ==========================================
   # ✅ JAZZMIN MODERN ADMIN THEME CONFIGURATION
   # ==========================================
   JAZZMIN_SETTINGS = {
       "site_title": "NigeriaInsight Admin",
       "site_header": "NigeriaInsight",
       "site_brand": "National Intelligence Command",
       "welcome_sign": "Welcome to the NigeriaInsight Command Center",
       "copyright": "NigeriaInsight 2026",
       "search_model": ["auth.User", "insight.UserProfile", "insight.Report"],
       "user_avatar": None,
       
       # ✅ TOP MENU (Keep it clean)
       "topmenu_links": [
           {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
           {"name": "Users", "url": "admin:auth_user_changelist"},
           {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
       ],
       
       # ✅ SIDEBAR (Organize by function)
       "show_sidebar": True,
       "navigation_expanded": True,
       "hide_apps": [],
       "hide_models": [],
       "order_with_respect_to": [
           "insight.Report",
           "insight.FieldVerification",
           "insight.AgentRegistrationRequest",
           "insight.UserProfile",
           "insight.FieldAgent",
           "auth",
       ],
       
       # ✅ MODERN DARK THEME WITH GOLD ACCENTS (Matching your Flutter App)
       "custom_css": None,
       "custom_js": None,
       "use_google_fonts_cdn": True,
       "show_ui_builder": False,
       
       "changeform_format": "horizontal_tabs",
       "changeform_format_overrides": {
           "auth.user": "collapsible",
           "auth.group": "vertical_tabs",
       },
       
       # Colors matching your app: Dark background, Gold/Yellow primary
       "related_modal_active": True,
   }

  # ==========================================
# ✅ JAZZMIN MODERN ADMIN THEME CONFIGURATION
# ==========================================
JAZZMIN_SETTINGS = {
    "site_title": "NigeriaInsight Admin",
    "site_header": "NigeriaInsight",
    "site_brand": "National Intelligence Command",
    "welcome_sign": "Welcome to the NigeriaInsight Command Center",
    "copyright": "NigeriaInsight 2026",
    "search_model": ["auth.User", "insight.UserProfile", "insight.Report"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Users", "url": "admin:auth_user_changelist"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "insight.Report",
        "insight.FieldVerification",
        "insight.AgentRegistrationRequest",
        "insight.UserProfile",
        "insight.FieldAgent",
        "auth",
    ],
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "related_modal_active": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-warning",
    "navbar": "navbar-dark navbar-primary",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-warning",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}