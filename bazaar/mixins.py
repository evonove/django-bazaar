from __future__ import unicode_literals

from itertools import chain

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django.views import generic

from crispy_forms.helper import FormHelper


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

    def get_context_data(self, **kwargs):
        context = super(SortableMixin, self).get_context_data(**kwargs)

        context["sort_fields"] = self.get_sort_fields_queries()
        context["current_sort_query"] = self.get_current_sort_query()
        context["current_sort_direction"] = self.get_current_sort_direction()

        return context


class SortableListView(SortableMixin, generic.ListView):
    def get_queryset(self):
        queryset = super(SortableMixin, self).get_queryset()

        if self.get_current_sort_field():
            queryset = queryset.order_by(self.get_current_sort_field())

        return queryset


class FilterMixin(object):
    """
    This mixin allows the user to specify a FilterSet class that filters the default queryset.
    Adds the filter form to the response context data with name `<model>_filter`.
    """
    filter_class = None
    filter_name = None

    def get_filter_class(self):
        if self.filter_class is None:
            raise ImproperlyConfigured("FilterMixin requires 'filter_class' to be defined")
        return self.filter_class

    def get_object_filter(self, queryset):
        """
        Return the instance of the filter class for the 'queryset'from ..mixins import FilterMixin
        """
        filter_class = self.get_filter_class()
        return filter_class(self.request.GET, queryset)

    def get_filter_name(self):
        """
        Returns a suitable name for the FilterSet instance to use in context data
        """
        if self.filter_name is None:
            return "%s%s" % (self.model._meta.object_name.lower(), "_filter")
        else:
            return self.filter_name

    def get_queryset(self):
        """
        Return a filtered queryset based on filter_class instance and request querystring parameters
        """
        queryset = super(FilterMixin, self).get_queryset()

        self.object_filter = self.get_object_filter(queryset)
        return self.object_filter.qs

    def get_context_data(self, **kwargs):
        context = super(FilterMixin, self).get_context_data(**kwargs)

        # Crispy helper to control how filter form is rendered
        helper = FormHelper()
        helper.form_tag = False
        helper.disable_csrf = True

        # attach helper to form instance
        self.object_filter.form.helper = helper

        # add filter object to context
        filter_name = self.get_filter_name()
        context[filter_name] = self.object_filter

        # add the querystring used to filter to the context data removing `page`
        # param so that we can easily integrate pagination and filtering
        query_filter = self.request.GET.copy()
        if "page" in query_filter:
            del query_filter["page"]

        context['query_filter'] = query_filter

        return context


class FilterSortableMixin(FilterMixin, SortableMixin):
    def get_filter_class(self):
        filter_class = super(FilterSortableMixin, self).get_filter_class()

        sort_fields = list(chain.from_iterable((x, "-%s" % x) for x in self.get_sort_fields()))

        class Filter(filter_class):
            order_by_field = self.sort_param

            class Meta(self.filter_class.Meta):
                order_by = sort_fields

            def get_ordering_field(self):
                field = super(Filter, self).get_ordering_field()
                return forms.ChoiceField(choices=field.choices, label="Ordering",
                                         required=False, widget=forms.HiddenInput)

        return Filter

    def get_context_data(self, **kwargs):
        context = super(FilterSortableMixin, self).get_context_data(**kwargs)

        if self.sort_param in context["query_filter"]:
            del context["query_filter"][self.sort_param]

        return context


class FilterSortableListView(FilterSortableMixin, generic.ListView):
    pass
