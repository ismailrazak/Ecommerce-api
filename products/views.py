from django.db.models import F

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, GenericViewSet

from cart.models import ProductQuantity
from products.models import Product, ProductImage
from products.permissions import IsCustomerOrNone, IsSellerOrNone
from products.serializers import CustomerProductSerializer, SellerProductSerializer, ProductImageSerializer
from django_filters import rest_framework as  filters
from rest_framework.mixins import RetrieveModelMixin,UpdateModelMixin,ListModelMixin

class CustomerProductViewSet(GenericViewSet,RetrieveModelMixin,UpdateModelMixin,ListModelMixin):
    serializer_class = CustomerProductSerializer
    queryset = Product.objects.all()
    permission_classes = IsCustomerOrNone,
    filter_backends = filters.DjangoFilterBackend,
    filterset_fields = ['category',]
    @action(detail=True,methods=["get",])
    def add_to_cart(self,request,pk=None):
        product=self.get_object()
        cart = request.user.cart
        if product.stock > 0:
            product_quantity =cart.product_quantity.filter(product__id=pk).first()
            if product_quantity:
                product_quantity.quantity=F('quantity')+1
                product_quantity.save()
            else:
                ProductQuantity.objects.create(cart=cart,product=product)
            product.stock=F('stock')-1
            product.save()
            return Response({'success':'The product has been successfully added to your cart.'},status=status.HTTP_200_OK)
        return Response({'error':'The product is out of stock.'},status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', ])
    def remove_item_from_cart(self, request, pk=None):
        cart = self.request.user.cart
        product_quantity=cart.product_quantity.filter(product__id=pk).first()
        if product_quantity:
            product = product_quantity.product
            if product_quantity.quantity >1:
                product_quantity.quantity=F('quantity')-1
                product_quantity.save()
                product.stock=F('stock')+1
                product.save()
                return Response({'success':'Item has been removed from your cart.'},status=status.HTTP_200_OK)
            else:
                product.stock = F('stock') + 1
                product.save()
                product_quantity.delete()
                return Response({'success': 'Item has been removed from your cart.'}, status=status.HTTP_200_OK)
        return Response({'error':'Item is not present in your cart.'},status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,methods=['get',])
    def buy_now(self,request,pk=None):
        pass



class SellerProductViewSet(ModelViewSet):
    serializer_class = SellerProductSerializer
    permission_classes = IsSellerOrNone,
    filter_backends = filters.DjangoFilterBackend,
    filterset_fields = ['category', ]
    def get_queryset(self):
        queryset = Product.objects.filter(sold_by=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(sold_by=self.request.user)

class ProductImageView(RetrieveUpdateDestroyAPIView):
    permission_classes = IsSellerOrNone,
    serializer_class =ProductImageSerializer
    queryset = ProductImage.objects.all()









#todo add buy all in cart too