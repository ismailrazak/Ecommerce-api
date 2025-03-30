from urllib.parse import urljoin

import requests
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from decouple import config
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView, CreateAPIView, GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_object_or_404

from accounts.views import logger
from cart.models import Cart
from cart.serializers import CartSerializer
from products.models import Product, Order
from products.permissions import IsCustomerOrNone
import razorpay

razorpay_client = razorpay.Client(
    auth=(config("RAZOR_ID"), config("RAZOR_SECRET")))



class CartView(APIView):
    permission_classes = IsCustomerOrNone,
    def get(self,request,pk=None):
        queryset =  get_object_or_404(Cart,user=self.request.user)
        serializer = CartSerializer(queryset,context={'request': request})
        return Response(serializer.data,status=status.HTTP_200_OK)

class CartItemRemoveAllView(APIView):
    permission_classes = IsCustomerOrNone,

    def post(self,request,pk=None):
        products = []
        cart = self.request.user.cart
        if not cart.products.all().exists():
            return Response({'error':'Your cart is already empty.'},status=status.HTTP_400_BAD_REQUEST)
        product_quantities =cart.product_quantity.all()
        for product_quantity in product_quantities:
                product =product_quantity.product
                products.append(product)
                product.stock = F('stock') + product_quantity.quantity
        Product.objects.bulk_update(products,['stock'])
        cart.products.clear()
        return Response({'success':'All Items has been removed successfully.'},status=status.HTTP_200_OK)

class CartBuyAllView(APIView):
    renderer_classes = TemplateHTMLRenderer,
    def get(self,request,pk=None):
        products = []
        create_orders=[]
        cart=self.request.user.cart
        if not cart.products.all().exists():
            return Response({'error':'Your cart is empty.'},status=status.HTTP_400_BAD_REQUEST)
        product_quantities = cart.product_quantity.all()
        total_price = product_quantities.aggregate(Sum('total_price'))['total_price__sum']
        razorpay_order = razorpay_client.order.create(dict(amount=int(total_price) * 100,
                                                           currency="INR"))
        razorpay_order_id = razorpay_order['id']
        for product_quantity in product_quantities:
            product = product_quantity.product
            order=Order(product=product,user=request.user,order_id=razorpay_order_id,quantity=product_quantity.quantity,final_price=product_quantity.total_price)
            create_orders.append(order)
        Order.objects.bulk_create(create_orders)
        cart.products.clear()
        callback_url = reverse("payment_handler")
        data = {"RAZOR_ID": config("RAZOR_ID"), "total_price": total_price, "user": request.user,
                "razorpay_order_id": razorpay_order_id, "callback_url": callback_url}
        return Response(data, template_name="cart_checkout.html")

