from __future__ import unicode_literals


class ActionWrapper(object):

    def __init__(self, action, name, slug, short_name):
        self.action = action
        self.name = name
        self.slug = slug
        self.short_name = short_name


class FilterWrapper(object):

    def __init__(self, filter, name):
        self.filter = filter
        self.name = name


class FormWrapper(object):

    def __init__(self, form, name):
        self.form = form
        self.name = name
