import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-ваш_ключ_должен_быть_длиннее_32_символов'
DEBUG = False
ALLOWED_HOSTS = [
    'brago22rus.pythonanywhere.com',
    '*.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Отключено для работы в iframe/приложении
]

ROOT_URLCONF = 'food_delivery_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'food_delivery_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/Brago22rus/my_shop/food_delivery_end/db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = '/home/Brago22rus/my_shop/food_delivery_end/staticfiles/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/Brago22rus/my_shop/food_delivery_end/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'SIGNING_KEY': SECRET_KEY,
    'ALGORITHM': 'HS256',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

CSRF_TRUSTED_ORIGINS = [
    'https://*.tunnel4.com',
    'https://*.xtunnel.ru',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://brago22rus.pythonanywhere.com',
    'https://*.pythonanywhere.com',
    'https://yookassa.ru',
    'https://*.yookassa.ru',
]
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============================================================
# БЕЗОПАСНОСТЬ (для работы в iframe/приложении)
# ============================================================
X_FRAME_OPTIONS = 'ALLOWALL'
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# ============================================================
# НАСТРОЙКИ EMAIL (GMAIL)
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'brago22rus@gmail.com'
EMAIL_HOST_PASSWORD = 'ijbyhwnulllspvzb'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_EMAIL = 'Andreu.shalaev@yandex.ru'

# ============================================================
# 🆕 НАСТРОЙКИ ЮKassa (ПРЯМОЕ ЗНАЧЕНИЕ)
# ============================================================
YOOKASSA_SHOP_ID = '1402224'
YOOKASSA_SECRET_KEY = 'test_gP8UdkN__wEtH6POKa190erLKjtgs3Ka97VNYtkVlIY'
FRONTEND_URL = 'https://Brago22rus.pythonanywhere.com'

# ============================================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# ============================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'yookassa.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'yookassa': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'shop': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}