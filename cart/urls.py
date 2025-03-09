from django.urls import path

from . import views


urlpatterns = [
    path("",views.CartView.as_view()),
    path('remove_all_items/',views.CartItemRemoveAllView.as_view()),

    ]
