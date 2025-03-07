from django.urls import path

from . import views


urlpatterns = [
    path("",views.CartView.as_view()),
    path('remove_item/<int:pk>/',views.CartItemRemoveView.as_view()),

    ]
