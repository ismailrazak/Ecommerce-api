from django.db import transaction
from django.db.models import F
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView, CreateAPIView, GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_object_or_404

from cart.models import Cart
from cart.serializers import CartSerializer
from products.models import Product
from products.permissions import IsCustomerOrNone

class CartView(APIView):
    permission_classes = IsCustomerOrNone,
    def get(self,request,pk=None):
        queryset =  get_object_or_404(Cart,user=self.request.user)
        serializer = CartSerializer(queryset,context={'request': request})
        return Response(serializer.data,status=status.HTTP_200_OK)

class CartItemRemoveAllView(APIView):
    permission_classes = IsCustomerOrNone,


    def post(self,request,pk=None):
        product_ids = []
        product_stock = []
        cart = self.request.user.cart
        if not cart.products.all().exists():
            return Response({'error':'Your cart is already empty.'},status=status.HTTP_400_BAD_REQUEST)
        product_quantities =cart.product_quantity.all()
        for product_quantity in product_quantities:
            product_ids.append(product_quantity.product_id)
            product_stock.append(product_quantity.quantity)
        products=Product.objects.filter(id__in=product_ids)
        @transaction.atomic
        def _product_stock_save():
            """
            using transaction.atomic to speed up individual saves.
            :return: None
            """
            for product, stock in zip(products, product_stock):
                product.stock = F('stock') + stock
                product.save()
        _product_stock_save()
        cart.products.clear()
        return Response({'success':'All Items has been removed successfully.'},status=status.HTTP_200_OK)
