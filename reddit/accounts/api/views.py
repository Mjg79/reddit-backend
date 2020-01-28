from rest_framework import viewsets, generics, exceptions, status
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from accounts.api.auth import Authentication
from django.utils.html import strip_tags
from django.contrib.auth import user_logged_in, user_logged_out
from accounts.models import User
from django.db import transaction
from accounts.api.serializers import LoginSerializer, UserSerializer


class UserView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # validate user input
        serializer.is_valid(raise_exception=True)

        user = User.objects.update_or_create(
            phone=serializer.validated_data['phone'],
            defaults=dict(username=serializer.validated_data['username'])
        )[0]
        user.set_password(serializer.validated_data['password'])
        user.first_name = strip_tags(serializer.validated_data.get('first_name', ''))
        user.last_name = strip_tags(serializer.validated_data.get('last_name', ''))
        user.save()

        return Response(
            data=serializer.validated_data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.validated_data)
        )


class LoginView(generics.CreateAPIView):

    permission_classes = [AllowAny]
    queryset = User.objects.none()
    serializer_class = LoginSerializer

    def authenticate_user(self, username, password):

        with transaction.atomic():
            user, created = Authentication().authenticate_credentials(userid=username, password=password)
            #  token will be needed
        user_logged_in.send(sender=user.__class__, request=self.request, user=user)
        return 'sss'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        full_token = self.authenticate_user(serializer.data['username'], serializer.data['password'])
        return Response(
            data={'token': full_token},
            status=status.HTTP_200_OK,
            headers=self.get_success_headers(serializer.data)
        )
