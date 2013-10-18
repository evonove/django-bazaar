from __future__ import unicode_literals

from bazaar.warehouse.models import Warehouse, RealGood, Movement
from bazaar.settings import bazaar_settings

from moneyed import Money

from ..base import BaseTestCase
from ..models import Good


class TestWarehouse(BaseTestCase):
    def test_model(self):
        warehouse = Warehouse(name="a warehouse")
        self.assertEqual(str(warehouse), "a warehouse")

    def test_get_default_return_default_warehouse(self):
        warehouse = Warehouse.objects.get_default()
        self.assertEqual(bazaar_settings.DEFAULT_WAREHOUSE_ID, warehouse.id)


class TestRealGood(BaseTestCase):
    def tearDown(self):
        Good.objects.all().delete()
        RealGood.objects.all().delete()

    def test_model(self):
        good = Good.objects.create(name="a good")
        real_good = RealGood(uid="fake-uid", good=good, warehouse=Warehouse.objects.get_default())
        self.assertEqual(str(real_good), "Real good fake-uid - 'a good' in Default")

    def test_price_is_converted_to_default_currency(self):
        # create a good
        good = Good.objects.create(name="a good")

        real_good = RealGood(uid="fake-uid", good=good, warehouse=Warehouse.objects.get_default())
        real_good.price = Money(1.0, "USD")
        real_good.save()

        self.assertEqual(real_good.price, Money(0.74, "EUR"))
        self.assertEqual(real_good.original_price, Money(1.0, "USD"))

    def test_defaults_currency(self):
        warehouse = Warehouse.objects.create(name="a warehouse")
        good = Good.objects.create(name="a good")
        real_good = RealGood.objects.create(
            good=good, price=0.0, warehouse=warehouse)

        self.assertEqual(real_good.price.currency.code, "EUR")


class TestMovement(BaseTestCase):
    def tearDown(self):
        Good.objects.all().delete()
        RealGood.objects.all().delete()
        Movement.objects.all().delete()

    def test_movement_str(self):
        w = Warehouse.objects.create(name="a warehouse")
        g = Good.objects.create(name="a good")
        rg = RealGood.objects.create(price=1.0, original_price=1.0, uid='00000', warehouse=w,
                                     good=g)
        m = Movement.objects.create(quantity=1, agent='test', reason='testing purposes',
                                    warehouse=w, good=rg)
        expected = 'Movement from test in warehouse a warehouse: 1.0000'
        self.assertEqual(expected, str(m))
