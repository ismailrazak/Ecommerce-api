from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("all_products", views.CustomerProductViewSet)
router.register("seller_products", views.SellerProductViewSet, basename="products")

urlpatterns = [
    path(
        "product_image/<int:pk>",
        views.ProductImageView.as_view(),
        name="product_image_detail",
    ),
    path(
        "product_review_create/<str:pk>",
        views.ProductReviewCreateView.as_view(),
        name="product_review_create",
    ),
    path(
        "product_review/<str:pk>",
        views.ProductReviewView.as_view(),
        name="product_review",
    ),
    path("hot_deals/<str:category>", views.HotDealsView.as_view()),
    path("payment_handler/", views.PaymentHandler.as_view(), name="payment_handler"),
]
urlpatterns += router.urls
