from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserRegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
from authuser.serializers import UserLoginSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.decorators import action

class RegisterViewSet(CreateModelMixin,GenericViewSet):
    serializer_class = UserRegisterSerializer



class LoginViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = UserLoginSerializer  # default

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)