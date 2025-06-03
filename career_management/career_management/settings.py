"""
Django settings for career_management project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Chargement .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Sécurité
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY is not set or empty. Check your .env file.")

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'votre-domaine.com']

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = 'email'
AUTH_USER_MODEL = 'management.CustomUser'

# Applications
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'dj_rest_auth',
    'rest_framework.authtoken',
    'management',
    'django_extensions',
    'corsheaders',
    'csp',  # Content Security Policy
]

# Middleware
MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'career_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'career_management.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localisation
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (),
    'DEFAULT_PERMISSION_CLASSES': (),
}

# =============================================================================
# CONFIGURATION SÉCURITÉ - CORRIGÉE POUR ZAP
# =============================================================================

# Headers de sécurité HTTP
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Configuration HTTPS (désactivée pour développement HTTP)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0  # Désactivé pour HTTP
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # Désactivé pour HTTP
SECURE_HSTS_PRELOAD = False  # Désactivé pour HTTP

# Cookies sécurisés (adaptés pour HTTP)
SESSION_COOKIE_SECURE = False  # False pour HTTP
CSRF_COOKIE_SECURE = False     # False pour HTTP
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# =============================================================================
# CONTENT SECURITY POLICY - CONFIGURATION CORRIGÉE (django-csp >= 4.0)
# =============================================================================

# Configuration CSP avec la nouvelle syntaxe django-csp 4.0+
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'", "http://localhost:3000"),
        'script-src': (
            "'self'", 
            "'unsafe-inline'", 
            "'unsafe-eval'",  # Pour React dev
            "http://localhost:3000",
            "https://cdnjs.cloudflare.com"
        ),
        'style-src': (
            "'self'", 
            "'unsafe-inline'",
            "http://localhost:3000", 
            "https://fonts.googleapis.com"
        ),
        'font-src': ("'self'", "https://fonts.gstatic.com"),
        'img-src': ("'self'", "data:", "blob:"),
        'connect-src': (
            "'self'",
            "http://localhost:3000",
            "http://localhost:8000",
            "ws://localhost:3000"  # WebSocket pour React hot reload
        ),
        'frame-ancestors': ("'none'",),  # Corrige l'alerte "frame-ancestors"
        'form-action': ("'self'",),      # Corrige l'alerte "form-action"
    }
}

# Rapport CSP en mode développement (optionnel)
if DEBUG:
    CONTENT_SECURITY_POLICY['REPORT_ONLY'] = False  # False pour appliquer, True pour tester seulement

# =============================================================================
# CORS - CONFIGURATION POUR REACT
# =============================================================================

FRONTEND_URL = 'http://localhost:3000'
CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Sécurité : seulement les origins autorisées

# Headers CORS autorisés
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('benalgiaoumaima040@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('xmcu jiel ankn hljq')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'security.log'),
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        # Logger pour CSP violations
        'csp': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'