from django.urls import path

from accounts import views

urlpatterns = [
    path(
        "register/customer",
        views.CustomerRegisterView.as_view(),
        name="register_customer",
    ),
    path("register/seller", views.SellerRegisterView.as_view(), name="register_seller"),
    path(
        "account_detail/<str:username>",
        views.AccountDetailView.as_view(),
        name="account_detail",
    ),
]
