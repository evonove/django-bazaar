from __future__ import unicode_literals

import django.dispatch


incoming_movement = django.dispatch.Signal(providing_args=["movement"])
outgoing_movement = django.dispatch.Signal(providing_args=["movement"])
