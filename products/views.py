from django.db.models import F
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, GenericViewSet

from products.models import Product
from products.permissions import IsCustomerOrNone, IsSellerOrNone
from products.serializers import CustomerProductSerializer, SellerProductSerializer


class CustomerProductViewSet(ReadOnlyModelViewSet):
    serializer_class = CustomerProductSerializer
    queryset = Product.objects.all()
    permission_classes = IsCustomerOrNone,

    @action(detail=True,methods=["get",])
    def add_to_cart(self,request,pk=None):
        product=self.get_object()
        if product.stock > 0:
            cart = request.user.cart
            cart.products.add(product)
            cart.save()
            product.stock=F('stock')-1
            product.save()
            return Response({'success':'The product has been successfully added to your cart.'},status=status.HTTP_200_OK)
        return Response({'error':'The product is out of stock.'},status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,methods=['get',])
    def buy_now(self,request,pk=None):
        pass

class SellerProductViewSet(ModelViewSet):
    serializer_class = SellerProductSerializer
    permission_classes = IsSellerOrNone,

    def get_queryset(self):
        queryset = Product.objects.filter(sold_by=self.request.user)
        return queryset


