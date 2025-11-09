from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer
from authuser.serializers import UserLoginSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from .serializers import AccountSerializer
from .models import Account


class AccountViewSet(mixins.ListModelMixin,GenericViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

class RegisterViewSet(CreateModelMixin,GenericViewSet):
    serializer_class = UserRegisterSerializer

class LoginViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = UserLoginSerializer  # default

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)