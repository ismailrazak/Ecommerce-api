from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from accounts.permissions import IsTheSameUserOrNone
from accounts.serializers import SellerAccountDetailSerializer, CustomerAccountDetailSerializer, \
     UserRegistrationSerializer
from dj_rest_auth.registration.views import RegisterView

from cart.models import Cart


#
# class CustomerRegistrationView(CreateAPIView):
#     serializer_class = CustomerRegistrationSerializer
#     queryset = get_user_model().objects.all()
#
#
# class SellerRegistrationView(CreateAPIView):
#     serializer_class = SellerRegistrationSerializer
#     queryset = get_user_model().objects.all()


class AccountDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = IsTheSameUserOrNone,
    queryset = get_user_model().objects.all()
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.request.user.groups.filter(name='sellers').exists():
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

        customer_group = Group.objects.get(name='customers')
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

        seller_group = Group.objects.get(name='sellers')
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