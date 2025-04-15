from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework.test import APIClient, APITestCase

from cart.models import Cart, ProductQuantity
from main import settings
from products.models import Product, Review
from products.tasks import ai_summary_review_task, hot_deals_task


class TestProductApp(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        customer_group = Group.objects.create(name="customers")
        seller_group = Group.objects.create(name="sellers")
        cls.customer = mixer.blend(settings.AUTH_USER_MODEL, username="test_customer")
        cls.customer.set_password("test")
        cls.customer.save()
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPAGATES = True
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

    def test_sellers_products_list_view(self):
        response = self.client.get(
            reverse("products-list"), headers=self.seller_headers
        )
        print(response.json())
        assert response.status_code == 200
        assert response.json()["results"][0]["name"] == self.test_product.name

    def test_sellers_product_create(self):
        test_image_url = "media/media/profiles/images/customer1_ba9c3c19-2aed-4292-b8e1-938d65d94752/blank-profile-picture-973460_640.png"
        test_images = [
            SimpleUploadedFile(
                name=f"test_image_{i}.png",
                content=open(test_image_url, "rb").read(),
                content_type="image/png",
            )
            for i in range(3)
        ]
        data = {
            "name": "product1",
            "description": "ho",
            "price": 100,
            "discount_percentage": 10,
            "stock": 10,
            "uploaded_images": test_images,
            "category": "ED",
        }
        response = self.client.post(
            reverse("products-list"), data=data, headers=self.seller_headers
        )
        print(response.json())
        assert response.status_code == 201
        assert response.json()["name"] == data["name"]

    def test_customer_review_create(self):
        data = {"description": "ho"}
        response = self.client.post(
            reverse("product_review_create", kwargs={"pk": self.test_product.id}),
            data=data,
            headers=self.customer_headers,
        )
        print(response.json())
        assert response.status_code == 201

    def test_ai_summary_celery_review_task(self):
        data = {
            "description": "I'm thoroughly impressed with this phone! The camera quality is exceptional, and it offers great value for money. I've been using it since November 24, and after five months, I can confidently say it's a must-buy. The phone runs smoothly, with seamless touch functionality and excellent sound quality."
        }
        response = self.client.post(
            reverse("product_review_create", kwargs={"pk": self.test_product.id}),
            data=data,
            headers=self.customer_headers,
        )

        result = ai_summary_review_task.apply(args=[self.test_product.id])
        print(result)
        assert result.status == "SUCCESS"

    def test_hot_deals_task(self):
        result = hot_deals_task.apply()
        assert result.status == "SUCCESS"
