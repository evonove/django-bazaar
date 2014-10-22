from django.test import TestCase
from bazaar.goods.forms import ProductForm
from tests.factories import ProductFactory


class MyTests(TestCase):

    def setUp(self):
        self.product = ProductFactory(ean="123456789")
        self.product.save()

    def test_ean_uniqueness_validator_fails_if_ean_already_exists(self):
        form_data = {
            'name': 'test product',
            'ean': "123456789",
            'price_0': self.product.price.amount,
            'price_1': self.product.price.currency
        }
        form = ProductForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_ean_uniqueness_validator_passes_if_ean_does_not_exist(self):
        form_data = {
            'name': 'test product',
            'ean': "324234432",
            'price_0': self.product.price.amount,
            'price_1': self.product.price.currency
        }
        form = ProductForm(data=form_data)
        self.assertEqual(form.is_valid(), True)
