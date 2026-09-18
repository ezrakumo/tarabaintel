import os
from pathlib import Path
import dj_database_url
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ 1. SECURE SECRET KEY: Read from Render Environment Variables
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-key-for-local-dev-only')

# ✅ 2. SECURE DEBUG: Strictly controlled by Environment Variable
DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']

# ✅ 3. SECURE HOSTS: Only allow your Render domain and local testing
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
if 'tarabaintel-ai.onrender.com' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('tarabaintel-ai.onrender.com')

# ... [KEEP YOUR INSTALLED_APPS AND MIDDLEWARE EXACTLY AS THEY ARE] ...

# ✅ 4. SECURE PROXY SETTINGS: Tell Django it's behind Render's HTTPS load balancer
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# ✅ 5. SECURE COOKIES: Prevent session hijacking over HTTP
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ... [KEEP YOUR DATABASE CONFIGURATION AS IS, it already uses os.environ.get('DATABASE_URL')] ...

# ✅ 6. SECURE EMAIL: Read from Environment Variables
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your_email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your_app_password')

# Tell Django where the PostGIS mapping libraries are located on Windows (Local only)
if os.name == 'nt':
    os.environ['PATH'] = r'C:\Program Files\PostgreSQL\18\bin' + os.pathsep + os.environ.get('PATH', '')
    GDAL_LIBRARY_PATH = r'C:\Program Files\PostgreSQL\18\bin\libgdal-35.dll'
    GEOS_LIBRARY_PATH = r'C:\Program Files\PostgreSQL\18\bin\libgeos_c.dll'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
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

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ MUST BE AT THE VERY TOP
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
        'DIRS': [],
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
# ✅ FIXED: Changed from 'tarabaintel_ai' to 'tarabaintel' to match your actual folder name!
ASGI_APPLICATION = 'tarabaintel.asgi.application'

# Database Configuration
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
# Email Configuration
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'ezrakumo@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '#MYGMAIL1@.kure2#')

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Password validation
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

# ==========================================
# CORS SETTINGS (Cleaned up, no duplicates)
# ==========================================
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = ['accept', 'accept-encoding', 'authorization', 'content-type', 'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with']
# ✅ SECURE HOSTS: Allow Render domain AND local testing
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Force-add these to prevent local testing from being blocked
for host in ['localhost', '127.0.0.1', 'tarabaintel-ai.onrender.com']:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)
# ==========================================
# JWT AUTHENTICATION SETTINGS
# ==========================================
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

# ==========================================
# EMAIL CONFIGURATION
# ==========================================
# ✅ BULLETPROOF GMAIL SMTP CONFIGURATION FOR RENDER
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Read credentials from Render Environment Variables
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ✅ Weekly Forecast Recipients
WEEKLY_FORECAST_RECIPIENTS = os.environ.get(
    'WEEKLY_FORECAST_RECIPIENTS', 
    'admin@tarabaintel.gov.ng,ops@tarabaintel.gov.ng'
).split(',')

# ==========================================
# CHANNELS / WEBSOCKET SETTINGS
# ==========================================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
