# flake8: noqa
import django

if django.VERSION < (1, 6):
    from django.db.transaction import commit_on_success as atomic
else:
    from django.db.transaction import atomic


if django.VERSION < (1, 7):
    from django.db.models.signals import post_syncdb as post_migrate
else:
    from django.db.models.signals import post_migrate
