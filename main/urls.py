"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from allauth.account.views import ConfirmEmailView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import GoogleLogin, GoogleLoginCallback, LoginPage

api_urlpatterns = [
    path("products/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("", include("search.urls")),
]

auth_urlpatterns = [
    path("", include("accounts.urls")),
    path("session_login/", include("rest_framework.urls")),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("", include("dj_rest_auth.urls")),
    # path('', include('dj_rest_auth.registration.urls')),
    path("google/login/", LoginPage.as_view(), name="login"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path(
        "google/callback/",
        GoogleLoginCallback.as_view(),
        name="google_login_callback",
    ),
]

urlpatterns = [
    # add the below path to resolve placeholder issue for email confirmation.
    re_path(
        r"^auth/account-confirm-email/(?P<key>[-:\w]+)/$",
        ConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    path("admin/", admin.site.urls),
    path("auth/", include(auth_urlpatterns)),
    path("", include(api_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
