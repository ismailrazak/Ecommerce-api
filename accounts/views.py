from urllib.parse import urljoin

import requests
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import RegisterView, SocialLoginView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsTheSameUserOrNone
from accounts.serializers import (
    CustomerAccountDetailSerializer,
    SellerAccountDetailSerializer,
    UserRegistrationSerializer,
)
from cart.models import Cart


class LoginPage(View):
    """
    This holds th google signup link since i dont have a frontend.
    """

    def get(self, request, *args, **kwargs):
        return render(
            request,
            "pages/login.html",
            {
                "google_callback_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
                "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            },
        )


class CustomGoogleOAuth2Client(OAuth2Client):
    """
    using a custom google oauth clinet cause of a bug .
    """

    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        _scope,
        scope_delimiter=" ",
        headers=None,
        basic_auth=False,
    ):
        super().__init__(
            request,
            consumer_key,
            consumer_secret,
            access_token_method,
            access_token_url,
            callback_url,
            scope_delimiter,
            headers,
            basic_auth,
        )


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = CustomGoogleOAuth2Client


class GoogleLoginCallback(APIView):
    """
    gives access token in return for a code google generates. also creates a
    cart for the user.
    """

    def get(self, request, *args, **kwargs):

        code = request.GET.get("code")

        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        token_endpoint_url = urljoin(
            "https://web-production-cc964.up.railway.app", reverse("google_login")
        )
        response = requests.post(
            url=token_endpoint_url,
            data={
                "code": code,
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "grant_type": "authorization_code",
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            },
        )
        # creates a customer from the google login
        user_data = response.json()
        user_id = user_data["user"]["pk"]
        user = get_user_model().objects.filter(id=user_id).first()
        customer_group = Group.objects.get(name="customers")
        user.groups.add(customer_group)
        created, cart = Cart.objects.get_or_create(user=user)
        return Response(response.json())


class AccountDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsTheSameUserOrNone,)
    queryset = get_user_model().objects.all()
    lookup_field = "username"

    def get_serializer_class(self):
        if self.request.user.groups.filter(name="sellers").exists():
            return SellerAccountDetailSerializer
        return CustomerAccountDetailSerializer


class CustomerRegisterView(RegisterView):
    """
    Using RegisterView to overwrite create method to add user to group and cart.
    Overwrite serializer_class or it will default from settings.
    rest all is same as super create method.
    """

    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)
        # adding these 3 lines below for adding cart.
        customer_group = Group.objects.get(name="customers")
        user.groups.add(customer_group)
        Cart.objects.create(user=user)

        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        return response


class SellerRegisterView(RegisterView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        overwrite the create method to add the user to seller group.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)

        seller_group = Group.objects.get(name="sellers")
        user.groups.add(seller_group)

        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        return response
