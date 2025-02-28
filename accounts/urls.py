from django.urls import path

from accounts import views

urlpatterns = [
    path('register/customer',views.CustomerRegistrationView.as_view()),
    path('register/seller',views.SellerRegistrationView.as_view()),
    path('account_detail/<str:username>',views.AccountDetailView.as_view()),
]
