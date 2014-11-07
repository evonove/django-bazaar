from __future__ import unicode_literals

from django.db import models
from model_utils.managers import InheritanceQuerySetMixin


class PublishingsQuerySet(InheritanceQuerySetMixin, models.QuerySet):
    pass
