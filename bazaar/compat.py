import django

if django.get_version() < (1, 6):
    from django.db.transaction import commit_on_success as atomic
else:
    from django.db.transaction import atomic