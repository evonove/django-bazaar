from __future__ import unicode_literals

from django.utils import six
from django.utils.translation import ugettext as _

import django_filters


class BaseFilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(BaseFilterSet, self).__init__(*args, **kwargs)

        # this is a workaround for issue https://github.com/alex/django-filter/issues/45
        for name, _filter in six.iteritems(self.filters):
            if isinstance(_filter, django_filters.ChoiceFilter):
                # Add "---------" entry to choice fields.
                _filter.extra['choices'] = tuple([("", _("---------")), ] +
                                                 list(_filter.extra['choices']))
