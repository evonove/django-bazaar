from __future__ import unicode_literals

from django import template
from ..models import Publishing


register = template.Library()


@register.assignment_tag
def main_publishings(listing):
    return Publishing.objects.main_publishings(listing)