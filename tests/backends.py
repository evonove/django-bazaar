from __future__ import unicode_literals

from djmoney_rates.backends import BaseRateBackend


class RateBackend(BaseRateBackend):
    source_name = "a source"
    base_currency = "USD"

    def get_rates(self):
        return {"USD": 1, "EUR": 0.74}
