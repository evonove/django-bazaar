from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django.views import generic


class TemplateNamePrefixMixin(object):
    """
    This mixin prepend `template_prefix` to template names
    """
    template_prefix = None

    def get_template_names(self):
        names = super(TemplateNamePrefixMixin, self).get_template_names()

        if self.template_prefix:
            return ["%s/%s" % (self.template_prefix, name) for name in names]
        else:
            return names


class BazaarPrefixMixin(TemplateNamePrefixMixin):
    template_prefix = "bazaar"


class SortableMixin(object):
    sort_fields = None
    sort_param = "order_by"

    def get_sort_fields(self):
        if self.sort_fields is None:
            raise ImproperlyConfigured("SortableMixin requires 'sort_fields' to be defined")
        else:
            return self.sort_fields

    def get_current_sort_field(self):
        return self.request.GET.get(self.sort_param, "")

    def get_current_sort_query(self):
        current_sort_field = self.get_current_sort_field()
        if current_sort_field:
            qdict = QueryDict("", mutable=True)
            qdict.update({self.sort_param: current_sort_field})
            return qdict.urlencode()

    def get_current_sort_direction(self):
        field = self.get_current_sort_field()
        return "-" if field.startswith("-") else ""

    def get_sort_direction(self, sort_field):
        if self.is_current(sort_field):
            return self.toggle_direction(self.get_current_sort_direction())

        return ""

    def toggle_direction(self, direction):
        return "-" if direction == "" else ""

    def is_current(self, sort_field):
        current = self.get_current_sort_field().lstrip("-")
        return current == sort_field

    def get_sort_fields_queries(self):
        sort_fields_queries = {}
        for sort_field in self.get_sort_fields():
            sort_direction = self.get_sort_direction(sort_field)

            qdict = QueryDict("", mutable=True)
            qdict.update({self.sort_param: sort_direction + sort_field})

            sort_fields_queries[sort_field] = {
                "query": qdict.urlencode(),
                "is_current": self.is_current(sort_field),
            }

        return sort_fields_queries


class SortableListView(SortableMixin, generic.ListView):
    def get_queryset(self):
        queryset = super(SortableMixin, self).get_queryset()

        if self.get_current_sort_field():
            queryset = queryset.order_by(self.get_current_sort_field())

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SortableMixin, self).get_context_data(**kwargs)

        context["sort_fields"] = self.get_sort_fields_queries()
        context["current_sort_query"] = self.get_current_sort_query()
        context["current_sort_direction"] = self.get_current_sort_direction()

        return context
