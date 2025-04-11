import logging

from celery.concurrency import custom
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework.test import APIClient, APITestCase

from cart.models import Cart, ProductQuantity
from products.models import Order, Product

logger = logging.getLogger("accounts.test")


class TestAccountsApp(APITestCase):

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

        cls.test_product = mixer.blend(Product, sold_by=cls.seller, stock=10)
        cls.order = mixer.blend(Order, user=cls.customer, product=cls.test_product)
        cls.customer.groups.add(customer_group)
        cls.seller.groups.add(seller_group)
        data = {"username": "test_customer", "password": "test"}
        customer_response = cls.client.post("/auth/token/", data=data)
        print(customer_response.json())
        access_token_customer = customer_response.json()["access"]
        cls.customer_headers = {"Authorization": "Bearer " + access_token_customer}

        data = {"username": "test_seller", "password": "test"}
        seller_response = cls.client.post("/auth/token/", data=data)
        access_token_seller = seller_response.json()["access"]
        cls.seller_headers = {"Authorization": "Bearer " + access_token_seller}

    def test_customer_register_view(self):
        test_image_url = "media/media/profiles/images/customer1_ba9c3c19-2aed-4292-b8e1-938d65d94752/blank-profile-picture-973460_640.png"
        test_image = SimpleUploadedFile(
            name="test_image.png",
            content=open(test_image_url, "rb").read(),
            content_type="image/png",
        )
        data = {
            "username": "test",
            "email": "testmail@gmail.com",
            "password1": "test123!",
            "password2": "test123!",
            "address": "test",
            "profile_photo": test_image,
        }
        response = self.client.post(reverse("register_customer"), data)
        assert response.status_code == 201
        assert response.json()["detail"] == "Verification e-mail sent."

    def test_seller_register_view(self):
        test_image_url = "media/media/profiles/images/customer1_ba9c3c19-2aed-4292-b8e1-938d65d94752/blank-profile-picture-973460_640.png"
        test_image = SimpleUploadedFile(
            name="test_image.png",
            content=open(test_image_url, "rb").read(),
            content_type="image/png",
        )
        data = {
            "username": "test_seller1",
            "email": "testmail@gmail.com",
            "password1": "test123!",
            "password2": "test123!",
            "address": "test",
            "profile_photo": test_image,
        }
        response = self.client.post(reverse("register_seller"), data)
        assert response.status_code == 201
        assert response.json()["detail"] == "Verification e-mail sent."
        user = get_user_model().objects.get(username="test_seller1")
        assert user.username == data["username"]

    def test_account_detail_for_customer(self):
        customer = self.customer
        response = self.client.get(
            reverse("account_detail", kwargs={"username": customer.username}),
            headers=self.customer_headers,
        )
        print(response.json())
        assert response.status_code == 200

    def test_account_customer_delete(self):
        Cart.objects.create(user=self.customer)
        product_original_quantity = self.test_product.stock
        print(product_original_quantity)
        cart_product = ProductQuantity.objects.create(
            cart=self.customer.cart, product=self.test_product, quantity=1
        )
        self.customer.delete()
        self.test_product.refresh_from_db()
        assert product_original_quantity + 1 == self.test_product.stock
