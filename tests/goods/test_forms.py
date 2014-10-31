from django.test import TestCase
from bazaar.goods.forms import ProductForm
from tests.factories import ProductFactory


class FormsTest(TestCase):

    def setUp(self):
        self.product = ProductFactory(ean="123456789")
        self.product2 = ProductFactory(ean="12345")
        self.product3 = ProductFactory(ean='')

    def test_ean_uniqueness_fails_if_ean_already_exists_when_creating(self):
        form_data = {
            'name': 'test product',
            'ean': "123456789",
            'price_0': self.product.price.amount,
            'price_1': self.product.price.currency
        }
        form = ProductForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_ean_uniqueness_passes_if_ean_does_not_exist_when_creating(self):
        form_data = {
            'name': 'test product',
            'ean': "324234432",
            'price_0': self.product.price.amount,
            'price_1': self.product.price.currency
        }
        form = ProductForm(data=form_data)
        self.assertEqual(form.is_valid(), True, form.errors)

    def test_ean_uniqueness_fails_if_ean_already_exists_when_updating(self):
        form_data = {
             'name': self.product.name,
             'ean': self.product2.ean,
             'price_0': self.product.price.amount,
             'price_1': self.product.price.currency
        }
        form = ProductForm(instance=self.product, data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_ean_uniqueness_passes_if_ean_does_not_exist_when_updating(self):
        form_data = {
             'name': self.product.name,
             'ean': '23892839932',
             'price_0': self.product.price.amount,
             'price_1': self.product.price.currency
        }
        form = ProductForm(instance=self.product, data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_ean_uniqueness_passes_if_not_updating_ean(self):
        form_data = {
            'name': self.product.name,
            'ean': self.product.ean,
            'price_0': self.product.price.amount,
            'price_1': self.product.price.currency
        }
        form = ProductForm(instance=self.product, data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_empty_ean_when_updating(self):
        form_data = {
            'name': self.product.name,
            'ean': '',
            'price_0': self.product.price.amount,
            'price_1': self.product.price.currency
        }
        form = ProductForm(instance=self.product, data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_empty_ean_when_inserting(self):
        form_data = {
            'name': self.product.name,
            'ean': '',
            'price_0': self.product.price.amount,
            'price_1': self.product.price.currency
        }
        form = ProductForm(data=form_data)
        self.assertEqual(form.is_valid(), True)