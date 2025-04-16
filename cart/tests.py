from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework.test import APIClient, APITestCase

from cart.models import Cart, ProductQuantity
from main import settings
from products.models import Product


class TestCartApp(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        customer_group = Group.objects.create(name="customers")
        seller_group = Group.objects.create(name="sellers")

        cls.customer = mixer.blend(settings.AUTH_USER_MODEL, username="test_customer")
        cls.customer.set_password("test")
        cls.customer.save()

        cls.seller = mixer.blend(settings.AUTH_USER_MODEL, username="test_seller")
        cls.seller.set_password("test")
        cls.seller.save()

        cls.customer.groups.add(customer_group)
        cls.seller.groups.add(seller_group)
        data = {"username": "test_customer", "password": "test"}
        customer_response = cls.client.post("/auth/token/", data=data)
        print(customer_response.json())
        access_token_customer = customer_response.json()["access"]
        cls.customer_headers = {"Authorization": "Bearer " + access_token_customer}

        cls.test_product = mixer.blend(Product, sold_by=cls.seller, stock=10)

        data = {"username": "test_seller", "password": "test"}
        seller_response = cls.client.post("/auth/token/", data=data)
        print(seller_response.json())
        access_token_seller = seller_response.json()["access"]
        cls.seller_headers = {"Authorization": "Bearer " + access_token_seller}
        Cart.objects.create(user=cls.customer)
        cart_product = ProductQuantity.objects.create(
            cart=cls.customer.cart, product=cls.test_product, quantity=1
        )

    def test_customer_cart_view(self):

        response = self.client.get(reverse("cart_view"), headers=self.customer_headers)
        print(response.json())
        assert response.status_code == 200
        assert response.json()["user"] == self.customer.username

    def test_remove_all_items_from_cart_view(self):
        response = self.client.post(
            reverse("remove_all_items"), headers=self.customer_headers
        )
        assert response.status_code == 204
        response = self.client.get(reverse("cart_view"), headers=self.customer_headers)
        print(response.json())
        assert response.json()["product"] == []
