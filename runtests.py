import sys

from django.conf import settings

settings.configure(
    DEBUG=True,
    USE_TZ=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
        }
    },
    ROOT_URLCONF="bazaar.urls",
    INSTALLED_APPS=[
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
        "bazaar.warehouse",
        "bazaar.listings",
        "bazaar.orders",
        "tests",
    ],
    SITE_ID=1,
    # Custom project settings go here
    DJANGO_MONEY_RATES={
        "DEFAULT_BACKEND": "tests.backends.RateBackend",
    },
)

try:
    from django_nose import NoseTestSuiteRunner
except ImportError:
    raise ImportError("To fix this error, run: pip install -r requirement-text.txt")

test_runner = NoseTestSuiteRunner(verbosity=1)
failures = test_runner.run_tests(["."])

if failures:
    sys.exit(failures)