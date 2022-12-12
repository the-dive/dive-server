"""
Django settings for dive project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
import environ
from pathlib import Path
import django.utils.encoding
from django.utils.encoding import force_str

django.utils.encoding.force_text = force_str

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APPS_DIR = BASE_DIR / "apps"

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str),
    DJANGO_ALLOWED_HOST=(str, "*"),
    POSTGRES_NAME=(str, "postgres"),
    POSTGRES_USER=(str, "postgres"),
    POSTGRES_PWD=(str, "postgres"),
    POSTGRES_HOST=(str, "db"),
    POSTGRES_PORT=(int, 5432),
    REDIS_URL=(str, "redis://redis:6379/0"),
    TIME_ZONE=(str, "Asia/Kathmandu"),
    # Static, Media configs
    DJANGO_STATIC_URL=(str, "/static/"),
    DJANGO_MEDIA_URL=(str, "/media/"),
    DJANGO_STATIC_ROOT=(str, os.path.join(BASE_DIR, "staticfiles")),
    DJANGO_MEDIA_ROOT=(str, os.path.join(BASE_DIR, "media")),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = ["server", env("DJANGO_ALLOWED_HOST")]


# Application definition

LOCAL_APPS = [
    "apps.file",
    "apps.core",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "graphene_django",
    "graphene_graphiql_explorer",
    "corsheaders",
] + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dive.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dive.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_NAME"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PWD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = env("TIME_ZONE")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = env("DJANGO_STATIC_URL")
MEDIA_URL = env("DJANGO_MEDIA_URL")
STATIC_ROOT = env("DJANGO_STATIC_ROOT")
MEDIA_ROOT = env("DJANGO_MEDIA_ROOT")

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"(^/api/.*$)|(^/media/.*$)|(^/graphql/$)"
CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "accept-encoding",
    "accept-language",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "sentry-trace",
)


GRAPHENE = {
    "ATOMIC_MUTATIONS": True,
    "SCHEMA": "dive.schema.schema",
    "SCHEMA_OUTPUT": "schema.json",
    "SCHEMA_INDENT": 2,
    "MIDDLEWARE": [],
}

GRAPHENE_DJANGO_EXTRAS = {
    "DEFAULT_PAGINATION_CLASS": "graphene_django_extras.paginations.PageGraphqlPagination",
    "DEFAULT_PAGE_SIZE": 20,
    "MAX_PAGE_SIZE": 50,
}


GRAPHENE_NODES_WHITELIST = (
    # __ double underscore nodes
    "__schema",
    "__type",
    "__typename",
    "file",
    "files",
    "dataset",
    "datasets",
)

CELERY_TIMEZONE = env("TIME_ZONE")
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

TEST_DIR = os.path.join(BASE_DIR, "dive/test_files")
