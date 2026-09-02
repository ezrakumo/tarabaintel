"""
Django settings for tarabaintel project.
"""
from pathlib import Path
import os
import dj_database_url
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-o**!299o2dq)d@s(+b!tuj0&i*fqet(@&@xt14(r892rp!43%0'

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Tell Django where the PostGIS mapping libraries are located on Windows
os.environ['PATH'] = r'C:\Program Files\PostgreSQL\18\bin' + os.pathsep + os.environ.get('PATH', '')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',  # <-- ADDED FOR JWT AUTH
    'django.contrib.gis',
    'corsheaders',
    'accounts',                  # <-- ADDED FOR USER MANAGEMENT
    'insight',
]

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

# Database Configuration
db_url = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
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

# WINDOWS-SPECIFIC FIX
if os.name == 'nt':
    GDAL_LIBRARY_PATH = r'C:\Program Files\PostgreSQL\18\bin\libgdal-35.dll'
    GEOS_LIBRARY_PATH = r'C:\Program Files\PostgreSQL\18\bin\libgeos_c.dll'

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

# Email
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

# CORS SETTINGS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = ['accept', 'accept-encoding', 'authorization', 'content-type', 'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with']

# ==========================================
# JWT AUTHENTICATION SETTINGS (ADDED)
# ==========================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}