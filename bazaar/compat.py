import django

if django.VERSION < (1, 6):
    from django.db.transaction import commit_on_success as atomic
else:
    from django.db.transaction import atomic