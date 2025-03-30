from urllib.parse import urljoin

import razorpay
import requests
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from decouple import config
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from cart.models import Cart
from cart.serializers import CartSerializer
from products.models import Order, Product
from products.permissions import IsCustomerOrNone

razorpay_client = razorpay.Client(auth=(config("RAZOR_ID"), config("RAZOR_SECRET")))


class CartView(APIView):
    permission_classes = (IsCustomerOrNone,)

    def get(self, request, pk=None):
        queryset = get_object_or_404(Cart, user=self.request.user)
        serializer = CartSerializer(queryset, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemRemoveAllView(APIView):
    permission_classes = (IsCustomerOrNone,)

    def post(self, request, pk=None):
        products = []
        cart = self.request.user.cart
        if not cart.products.all().exists():
            return Response(
                {"error": "Your cart is already empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product_quantities = cart.product_quantity.all()
        for product_quantity in product_quantities:
            product = product_quantity.product
            products.append(product)
            product.stock = F("stock") + product_quantity.quantity
        Product.objects.bulk_update(products, ["stock"])
        cart.products.clear()
        return Response(
            {"success": "All Items has been removed successfully."},
            status=status.HTTP_200_OK,
        )


class CartBuyAllView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, pk=None):
        products = []
        create_orders = []
        cart = self.request.user.cart
        if not cart.products.all().exists():
            return Response(
                {"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST
            )
        product_quantities = cart.product_quantity.all()
        total_price = product_quantities.aggregate(Sum("total_price"))[
            "total_price__sum"
        ]
        razorpay_order = razorpay_client.order.create(
            dict(amount=int(total_price) * 100, currency="INR")
        )
        razorpay_order_id = razorpay_order["id"]
        for product_quantity in product_quantities:
            product = product_quantity.product
            order = Order(
                product=product,
                user=request.user,
                order_id=razorpay_order_id,
                quantity=product_quantity.quantity,
                final_price=product_quantity.total_price,
            )
            create_orders.append(order)
        Order.objects.bulk_create(create_orders)
        callback_url = reverse("cart_payment_handler")
        data = {
            "RAZOR_ID": config("RAZOR_ID"),
            "total_price": total_price,
            "user": request.user,
            "razorpay_order_id": razorpay_order_id,
            "callback_url": callback_url,
        }
        return Response(data, template_name="cart_checkout.html")


class CartPaymentHandler(APIView):
    def post(self, request, pk=None):
        update_orders = []
        try:
            payment_id = request.data.get("razorpay_payment_id", "")
            razorpay_order_id = request.data.get("razorpay_order_id", "")
            signature = request.data.get("razorpay_signature", "")
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                orders = Order.objects.filter(order_id=razorpay_order_id)
                for order in orders:
                    order.payment_id = payment_id
                    update_orders.append(order)
                Order.objects.bulk_update(update_orders, ["payment_id"])
                user = orders[0].user
                user.cart.products.clear()
                return Response("payment success", status=status.HTTP_200_OK)
            else:
                return Response("payment fail", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                "payment exception fail", status=status.HTTP_400_BAD_REQUEST
            )
