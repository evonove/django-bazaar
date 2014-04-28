from __future__ import unicode_literals

import django.dispatch


incoming_movement = django.dispatch.Signal(providing_args=["movement"])
outgoing_movement = django.dispatch.Signal(providing_args=["movement"])

lost_and_found_changed = django.dispatch.Signal(providing_args=["product"])
supplier_changed = django.dispatch.Signal(providing_args=["product"])
storage_changed = django.dispatch.Signal(providing_args=["product"])
output_changed = django.dispatch.Signal(providing_args=["product"])
customer_changed = django.dispatch.Signal(providing_args=["product"])
