from django.db.models.signals import post_syncdb
from ..listings.stores.config import create_stores

post_syncdb.connect(create_stores)
