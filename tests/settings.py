from __future__ import absolute_import
from __future__ import unicode_literals

DEBUG = True

USE_TZ = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}

ROOT_URLCONF = "bazaar.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",

    "crispy_forms",
    "djmoney_rates",
    "stored_messages",
    "rest_framework",

    "bazaar",
    "bazaar.goods",
    "bazaar.listings",
    "bazaar.warehouse",
    "tests",
]

SITE_ID = 1

STATIC_URL = "/static/"

SECRET_KEY = "very_secret_key"

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Custom project settings go here
DJANGO_MONEY_RATES = {
    "DEFAULT_BACKEND": "tests.backends.RateBackend",
}
