from __future__ import unicode_literals

from django import template
from ..managers import PublishingManager


register = template.Library()


@register.assignment_tag
def get_active_or_last_completed_publishing(publishings):
    return PublishingManager().active_or_last_completed_publishing(publishings)