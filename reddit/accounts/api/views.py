from rest_framework import viewsets, generics, exceptions, status
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from .auth import Authentication
from django.utils.html import strip_tags
from django.contrib.auth import user_logged_in, user_logged_out
from accounts.models import User, Profile
from django.db import transaction
from .serializers import LoginSerializer, UserSerializer, AuthorSerializer, ProfileSerializer
from socials.api.serializers import ChannelSerializer
from socials.models import Channel


class UserView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_queryset(self):
        return [self.request.user]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.create(
                username=serializer.data['username'],
            )
            user.set_password(request.data['password'])
            user.save()
            Profile.objects.create(user=user)
            return Response(dict(), status=status.HTTP_201_CREATED)
        else:
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        if not data.get('email', None):
            return Response(status=status.HTTP_403_FORBIDDEN)
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.email = data.get('email', '')
        user.phone = data.get('phone', '')
        user.save()
        return Response(UserSerializer(instance=user).data, status=status.HTTP_200_OK)


class LoginView(generics.CreateAPIView):

    permission_classes = [AllowAny]
    queryset = User.objects.none()
    serializer_class = LoginSerializer

    def authenticate_user(self, username, password):

        with transaction.atomic():
            user, created = Authentication().authenticate_credentials(userid=username, password=password)
            #  token will be needed
        user_logged_in.send(sender=user.__class__, request=self.request, user=user)
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.authenticate_user(serializer.data['username'], serializer.data['password'])
        return Response(
            data=UserSerializer(instance=user).data,
            status=status.HTTP_200_OK,
            headers=self.get_success_headers(serializer.data)
        )


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        pk = request.query_params.get('id', None)
        if not pk:
            raise exceptions.NotFound
        return Response(
            data=ProfileSerializer(instance=Profile.objects.get(user__id=pk)).data, status=status.HTTP_200_OK
        )


class FollowView(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AuthorSerializer

    @action(detail=True, methods=['get'])
    def followers(self, request, pk):
        user = User.objects.get(id=pk)
        return Response(
            data=AuthorSerializer(
                instance=user.personal_profile.followed_by.all(), many=True, context={'user': user}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def followings(self, request, pk):
        user = User.objects.get(id=pk)
        return Response(
            data={
                'people': AuthorSerializer(
                    instance=user.followings_user.all().values_list('user', flat=True).distinct(), many=True
                ).data,
                'channels': ChannelSerializer(instance=user.followings_channel.all(), many=True).data,
            }
        )

    @action(detail=True, methods=['put'])
    def user(self, request, pk):
        profile = Profile.objects.get(user__id=pk)
        profile.followed_by.add(request.user)
        profile.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def channel(self, request, pk):
        channel = Channel.objects.get(id=pk)
        channel.followed_by.add(request.user)
        channel.save()
        return Response(status=status.HTTP_200_OK)








