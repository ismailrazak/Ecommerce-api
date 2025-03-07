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

class CartItemRemoveView(APIView):
    permission_classes = IsCustomerOrNone,


    def post(self,request,pk=None):
        cart = self.request.user.cart
        product = get_object_or_404(Product,id=pk)
        cart.products.remove(product)
        cart.save()
        product.stock=F('stock')+1
        product.save()
        return Response({'success':'Item has been removed sucessfully.'},status=status.HTTP_200_OK)
