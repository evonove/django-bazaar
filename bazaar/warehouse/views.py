from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView

from braces.views import LoginRequiredMixin

from ..mixins import BazaarPrefixMixin
from .forms import MovementInForm, MovementOutForm
from .utils import in_movement, out_movement


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


class MovementInFormView(MovementMixin, FormView):
    form_class = MovementInForm
    template_name = "warehouse/movement_in.html"
    success_url = reverse_lazy("bazaar:movement-in")

    def form_valid(self, form):
        product = form.cleaned_data["product"]
        quantity = form.cleaned_data["quantity"]
        price = form.cleaned_data["price"]
        notes = form.cleaned_data["notes"]

        in_movement(quantity, self.request.user, notes, product, price)

        return super(MovementInFormView, self).form_valid(form)


class MovementOutFormView(MovementMixin, FormView):
    form_class = MovementOutForm
    template_name = "warehouse/movement_out.html"
    success_url = reverse_lazy("bazaar:movement-out")

    def form_valid(self, form):
        product = form.cleaned_data["product"]
        quantity = form.cleaned_data["quantity"]
        notes = form.cleaned_data["notes"]

        out_movement(quantity, self.request.user, notes, product)

        return super(MovementOutFormView, self).form_valid(form)
