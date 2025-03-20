from django.urls import path

from . import views

urlpatterns = [
    path("search/<str:query>",views.SearchProductsView.as_view())
]