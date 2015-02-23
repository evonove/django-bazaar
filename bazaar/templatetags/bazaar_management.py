from __future__ import unicode_literals

from django import template

from ..listings.stores import stores_loader

register = template.Library()


@register.assignment_tag
def store_publishing_template(store_slug):
    return stores_loader.get_store_strategy(store_slug).get_store_publishing_template()


@register.assignment_tag
def store_publishing_list_template(store_slug):
    return stores_loader.get_store_strategy(store_slug).get_store_publishing_list_template()


@register.assignment_tag
def store_publishing_can_delete(store_slug):
    return True if stores_loader.get_store_strategy(store_slug).get_publishing_delete_action() else False


@register.assignment_tag
def store_publishing_can_update(store_slug):
    return True if stores_loader.get_store_strategy(store_slug).get_publishing_update_action() else False
