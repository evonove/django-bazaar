from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView

from braces.views import LoginRequiredMixin

from ..mixins import BazaarPrefixMixin
from . import api
from .forms import MovementForm


class MovementMixin(LoginRequiredMixin, BazaarPrefixMixin):
    def get_success_url(self):
        if "next" in self.request.GET:
            return self.request.GET.get("next")
        else:
            return super(MovementMixin, self).get_success_url()

    def get_initial(self):
        initial = super(MovementMixin, self).get_initial()

        product = self.request.GET.get("product")
        if product:
            initial["product"] = product

        return initial


class MovementFormView(MovementMixin, FormView):
    form_class = MovementForm
    template_name = "warehouse/movement.html"
    success_url = reverse_lazy("bazaar:movement")

    def form_valid(self, form):
        product = form.cleaned_data["product"]
        from_location = form.cleaned_data["from_location"]
        to_location = form.cleaned_data["to_location"]
        quantity = form.cleaned_data["quantity"]
        unit_price = form.cleaned_data["unit_price"]
        note = form.cleaned_data["note"]

        price_multiplier = unit_price / product.price

        product.move(from_location, to_location, quantity=quantity, price_multiplier=price_multiplier,
                     agent=self.request.user, note=note)

        return super(MovementFormView, self).form_valid(form)
