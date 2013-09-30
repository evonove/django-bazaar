from django.db.models import signals
from django.db import connections
from django.db import router
from django.core.management.color import no_style

from . import models as goods_app
from .models import PriceList


def create_default_pricelist(app, created_models, verbosity, db, **kwargs):
    """
    Create the default PriceList with id = 1.

    This command is based on `create_default_site` command from the django.contrib.site application
    """

    if PriceList in created_models and router.allow_syncdb(db, PriceList):
        if verbosity >= 2:
            print("Creating default PriceList object")
        PriceList(pk=1, name="Default").save(using=db)

        # We set an explicit pk instead of relying on auto-incrementation,
        # so we need to reset the database sequence. See #17415.
        sequence_sql = connections[db].ops.sequence_reset_sql(no_style(), [PriceList])
        if sequence_sql:
            if verbosity >= 2:
                print("Resetting sequence")
            cursor = connections[db].cursor()
            for command in sequence_sql:
                cursor.execute(command)

signals.post_syncdb.connect(create_default_pricelist, sender=goods_app)
