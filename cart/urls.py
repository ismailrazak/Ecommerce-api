from django.urls import path

from . import views


urlpatterns = [
    path("",views.CartView.as_view()),
    path('remove_all_items/',views.CartItemRemoveAllView.as_view()),
    path('buy_all_items/',views.CartBuyAllView.as_view()),
    path('cart_payment_handler/',views.CartPaymentHandler.as_view(),name='cart_payment_handler')
    ]
