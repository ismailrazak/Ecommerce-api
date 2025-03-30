import json

import razorpay
import redis
from decouple import config
from django.core.cache import cache
from django.db.models import F
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action, renderer_classes
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from cart.models import ProductQuantity
from products.models import Order, Product, ProductImage, Review
from products.permissions import IsCustomerOrNone, IsReviewerOrReadOnly, IsSellerOrNone
from products.serializers import (
    CustomerProductSerializer,
    ProductImageSerializer,
    ReviewSerializer,
    SellerProductSerializer,
)
from products.tasks import ai_summary_review_task

razorpay_client = razorpay.Client(auth=(config("RAZOR_ID"), config("RAZOR_SECRET")))


r = redis.Redis(
    host=config("REDIS_HOST", default="redis"),
    port=config("REDIS_PORT", default=6379),
    db=0,
    decode_responses=True,
)


class CustomerProductViewSet(
    GenericViewSet, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
):
    serializer_class = CustomerProductSerializer
    queryset = Product.objects.all()
    permission_classes = (IsCustomerOrNone,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = [
        "category",
    ]

    @action(
        detail=True,
        methods=[
            "get",
        ],
    )
    def add_to_cart(self, request, pk=None):
        product = self.get_object()
        cart = request.user.cart
        if product.stock > 0:
            product_quantity = cart.product_quantity.filter(product__id=pk).first()
            if product_quantity:
                product_quantity.quantity = F("quantity") + 1
                product_quantity.save()
            else:
                ProductQuantity.objects.create(cart=cart, product=product)
            product.stock = F("stock") - 1
            product.save()
            return Response(
                {"success": "The product has been successfully added to your cart."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "The product is out of stock."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=[
            "get",
        ],
    )
    def remove_item_from_cart(self, request, pk=None):
        cart = self.request.user.cart
        product_quantity = cart.product_quantity.filter(product__id=pk).first()
        if product_quantity:
            product = product_quantity.product
            if product_quantity.quantity > 1:
                product_quantity.quantity = F("quantity") - 1
                product_quantity.save()
                product.stock = F("stock") + 1
                product.save()
                return Response(
                    {"success": "Item has been removed from your cart."},
                    status=status.HTTP_200_OK,
                )
            else:
                product.stock = F("stock") + 1
                product.save()
                product_quantity.delete()
                return Response(
                    {"success": "Item has been removed from your cart."},
                    status=status.HTTP_200_OK,
                )
        return Response(
            {"error": "Item is not present in your cart."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=[
            "get",
        ],
        renderer_classes=[TemplateHTMLRenderer],
    )
    def buy_now(self, request, pk=None):

        product = self.get_object()
        if product.stock <= 0:
            return JsonResponse({"error": "product out of stock."})
        razorpay_order = razorpay_client.order.create(
            dict(amount=int(product.discounted_price) * 100, currency="INR")
        )
        razorpay_order_id = razorpay_order["id"]
        callback_url = reverse("payment_handler")
        Order.objects.create(
            user=request.user,
            order_id=razorpay_order_id,
            product=product,
            final_price=product.discounted_price,
        )

        data = {
            "RAZOR_ID": config("RAZOR_ID"),
            "product": product,
            "user": request.user,
            "razorpay_order_id": razorpay_order_id,
            "callback_url": callback_url,
        }
        return Response(data, template_name="checkout.html")


class PaymentHandler(APIView):
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
                order = Order.objects.filter(order_id=razorpay_order_id).first()
                product = order.product
                order.payment_id = payment_id
                order.save()
                product.stock = F("stock") - 1
                product.save()

                return Response("payment success", status=status.HTTP_200_OK)
            else:
                return Response("payment fail", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:

            return Response(
                "payment exception fail", status=status.HTTP_400_BAD_REQUEST
            )


class SellerProductViewSet(ModelViewSet):
    serializer_class = SellerProductSerializer
    permission_classes = (IsSellerOrNone,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = [
        "category",
    ]

    def get_queryset(self):
        queryset = Product.objects.filter(sold_by=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(sold_by=self.request.user)


class ProductImageView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsSellerOrNone,)
    serializer_class = ProductImageSerializer
    queryset = ProductImage.objects.all()


class ProductReviewView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (IsReviewerOrReadOnly,)
    queryset = Review.objects.all()


class ProductReviewCreateView(APIView):
    permission_classes = (IsCustomerOrNone,)

    def get(self, request, pk=None):
        product = Product.objects.filter(id=pk).first()
        serializer = CustomerProductSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk=None):
        product = Product.objects.filter(id=pk).first()
        description = request.data.get("description")
        reviewer = self.request.user
        if product.product_reviews.filter(reviewer=reviewer).exists():
            return Response(
                {"error": "You have already made a review for this product."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        review = Review.objects.create(
            product=product, reviewer=self.request.user, description=description
        )
        reviews_counter = r.incr(f"total_reviews_{product.id}")
        if reviews_counter == 5:
            ai_summary_review_task.delay(product.id)
            r.set(f"total_reviews_{product.id}", 0)
        return Response(
            {"success": "Review has been created successfully."},
            status=status.HTTP_201_CREATED,
        )


class HotDealsView(APIView):
    def get(self, request, category, pk=None):

        products = cache.get(f"category:{category}")
        if products:
            return Response(products, status=status.HTTP_200_OK)
        else:
            products = Product.objects.filter(category=category).order_by(
                "-discount_percentage"
            )[:50]
            serializer = CustomerProductSerializer(
                products, many=True, context={"request": request}
            )
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


# todo add db transaction to both of pays
