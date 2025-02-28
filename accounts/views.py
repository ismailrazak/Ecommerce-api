from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView

from accounts.permissions import IsTheSameUserOrNone
from accounts.serializers import CustomerRegistrationSerializer, SellerRegistrationSerializer,SellerAccountDetailSerializer,CustomerAccountDetailSerializer


class CustomerRegistrationView(CreateAPIView):
    serializer_class = CustomerRegistrationSerializer
    queryset = get_user_model().objects.all()


class SellerRegistrationView(CreateAPIView):
    serializer_class = SellerRegistrationSerializer
    queryset = get_user_model().objects.all()


class AccountDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = IsTheSameUserOrNone,
    queryset = get_user_model().objects.all()
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.request.user.groups.filter(name='sellers').exists():
            return SellerAccountDetailSerializer
        return CustomerAccountDetailSerializer

