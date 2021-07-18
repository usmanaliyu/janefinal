

from django.contrib import messages
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'en4)ftlfhpa2vz3tbb=&vp(%he=n52r@&e)dd%k-i^dd*7-fat'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'ckeditor',
    "ckeditor_uploader",
    "django.contrib.humanize",
    'crispy_forms',
    'django.contrib.sites',
    'django_countries',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    "paystack",
    "blog",
    "sorl.thumbnail",
    'django_filters',
    "taggit",
    'django_inlinecss',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    "taggit_serializer"
]

# paystack
PAYSTACK_PUBLIC_KEY = "pk_live_3b7b32232d4485c95cdc0c50f83acda3b6f523b1"
PAYSTACK_SECRET_KEY = "sk_live_1c2a919aca68e2a4fb2369cd828972d801a29d80"

# PAYSTACK_PUBLIC_KEY = "pk_test_6681e7fc29d2350d6f35f98ae14535747f541783"
# PAYSTACK_SECRET_KEY = "sk_test_eb983647781b4cdca3ba3be945637e1585059f71"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jane_new.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'jane_new.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "jane",
        "USER": 'postgres',
        "PASSWORD": 'austinforreal',
        'HOST': 'localhost',
        "PORT": ''
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 5,

        }
    },

    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'

USE_I18N = True

USE_L10N = True

USE_TZ = False


STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_dir')
]

# STATICFILES_DIRS = [
#   "/home/jane/jane/jane_new/static_dir"
# ]


STATIC_ROOT = os.path.join(BASE_DIR, 'assets')
# STATIC_ROOT = "/home/jane/jane/jane_new/static"


MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# MEDIA_ROOT = "/home/jane/jane/jane_new/media"

CKEDITOR_UPLOAD_PATH = "uploads/"


AUTHENTICATION_BACKENDS = [

    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

AUTH_USER_MODEL = 'core.CustomUser'

ACCOUNT_AUTHENTICATION_METHOD = "username_email"

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_LOGOUT_ON_GET = False

LOGIN_REDIRECT_URL = '/'

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_SESSION_REMEMBER = True


# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.zoho.com'
# EMAIL_HOST_USER = 'contact@janes-fashion.com'
# EMAIL_HOST_PASSWORD = 'janesfashion1A'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
# DEFAULT_FROM_EMAIL = 'contact@janes-fashion.com'


ACCOUNT_FORMS = {'signup': 'core.forms.CustomSignupForm'}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


REST_FRAMEWORK = {

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]

}

ACCOUNT_EMAIL_VERIFICATION ="optional"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000"

]

CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000"

]

CORS_ORIGIN_ALLOW_ALL = True


REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'core.serializers.UserRegistration',
    "PASSWORD_RESET_SERIALIZER": "dj_rest_auth.serializers.PasswordResetSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "dj_rest_auth.serializers.PasswordResetConfirmSerializer"
}


ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
