"""
Django settings for mentisparchment_docker project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import environ
import pymongo
import os
import sys
print('********** SETTINGS **********')
print("Python Version:\n {}".format(sys.version))
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True)
)

# reading .env file
environ.Env.read_env(os.path.join(BASE_DIR,".env"))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", " ")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
# ALLOWED_HOSTS = ['localhost' '127.0.0.1' '[::1]' '0.0.0.0' 'mongodb' '0.0.0.0:8000']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'api.search',
    'django_json_ld',
]
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'fe/css'),  # this is for
    os.path.join(BASE_DIR, 'fe/css/custom'),  # this is for
    os.path.join(BASE_DIR, "fe/js"),  # this is for
    os.path.join(BASE_DIR, "fe/js/custom"),  # this is for
    os.path.join(BASE_DIR, "fe/js/chart.js-2.9.4"),  # this is for
    os.path.join(BASE_DIR, "fe/js/chart.js-2.9.4/package/dist"),  # this is for
    os.path.join(BASE_DIR, "fe/html"),  # this is for
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = os.environ.get("DJANGO_ROOT_URL", "mentisparchment_docker.urls")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['static'],
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

WSGI_APPLICATION = 'mentisparchment_docker.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'ENFORCE_SCHEMA': True,
        'NAME': os.environ.get("MONGODB_DATABASE", "mentisparchment_docker"),
        'CLIENT':{
            'host': os.environ.get("MONGO_DB_HOST", "mongodb"),
            'port': int(os.environ.get("MONGO_DB_PORT", 27017)),
            'username': os.environ.get("MONGO_DB_USERNAME", 'root'),
            'password': os.environ.get("MONGO_DB_PASSWORD", 'mongoadmin'),
            'authSource':os.environ.get("MONGO_DB_AUTH_SOURCE", 'admin'),
            'authMechanism': os.environ.get("MONGO_DB_AUTH_MECH", 'SCRAM-SHA-1'),
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_URL = '/static/'
JSON_LD_DEFAULT_CONTEXT='http://www.w3.org/ns/anno.jsonld'

APPEND_SLASH=False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 20*60
