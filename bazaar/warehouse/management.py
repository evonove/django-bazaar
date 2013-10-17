from django.db.models import signals
from django.db import connections
from django.db import router
from django.core.management.color import no_style

from . import models as warehouse_app
from .models import Warehouse


def create_default_warehouse(app, created_models, verbosity, db, **kwargs):
    """
    Create the default Warehouse with id = 1.

    This command is based on `create_default_site` command from the django.contrib.site application
    """

    if Warehouse in created_models and router.allow_syncdb(db, Warehouse):
        if verbosity >= 2:
            print("Creating default PriceList object")
        Warehouse(pk=1, name="Default").save(using=db)

        # We set an explicit pk instead of relying on auto-incrementation,
        # so we need to reset the database sequence. See #17415.
        sequence_sql = connections[db].ops.sequence_reset_sql(no_style(), [Warehouse])
        if sequence_sql:
            if verbosity >= 2:
                print("Resetting sequence")
            cursor = connections[db].cursor()
            for command in sequence_sql:
                cursor.execute(command)

signals.post_syncdb.connect(create_default_warehouse, sender=warehouse_app)
