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
from .serializers import LoginSerializer, UserSerializer, AuthorSerializer, ProfileSerializer, UploadSerializer
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
        user = request.user
        # serializer = UploadSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # data = serializer.validated_data
        data = request.data
        if not data.get('email', None):
            raise exceptions.NotAcceptable('please enter an email')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.email = data.get('email', '')
        user.phone = data.get('phone', '')
        user.personal_profile.picture = data.get('picture', '')
        user.personal_profile.save()
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


class ProfileView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user__id=self.request.query_params.get('id', 0))

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        p1 = data.get('password1', '')
        p2 = data.get('password2', '')
        if not p1 or not p2 or p1 != p2:
            raise exceptions.NotAcceptable
        user.set_password(p1)
        user.save()
        return Response(dict(), status.HTTP_200_OK)


class FollowView(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AuthorSerializer

    @action(detail=True, methods=['get'])
    def followers(self, request, pk):
        user = User.objects.get(id=pk)
        return Response(
            data=AuthorSerializer(
                instance=user.personal_profile.followed_by.all(), many=True, context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def followings(self, request, pk):
        from socials.api.serializers import ChannelSerializer
        user = User.objects.get(id=pk)
        return Response(
            data={
                'people': AuthorSerializer(
                    instance=user.followings_user.all().values_list('user', flat=True).distinct(), many=True,
                    context={'request':request}
                ).data,
                'channels': ChannelSerializer(instance=user.followings_channel.all(), many=True).data,
            }
        )

    @action(detail=True, methods=['put'])
    def user(self, request, pk):
        from socials.models import Notification, NotifSituations
        from django.contrib.contenttypes.models import ContentType

        action = request.query_params.get('action', '')
        profile = Profile.objects.get(user__id=pk)
        if action == 'unfollow':
            profile.followed_by.remove(request.user)
        else:
            Notification.objects.create(
                situation=NotifSituations.FOLLOWED, for_user=profile.user, who=request.user,
                audience_id=request.user.id, audience_type=ContentType.objects.get(model='user')
            )
            profile.followed_by.add(request.user)
        profile.save()
        return Response(data=dict(), status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def channel(self, request, pk):
        channel = Channel.objects.get(id=pk)
        if request.query_params.get('action', '') == 'unfollow':
            channel.followed_by.remove(request.user)
        else:
            channel.followed_by.add(request.user)
        channel.save()
        return Response(data=dict(), status=status.HTTP_200_OK)


def get_verfy_code():
    import random
    s = ''
    for _ in range(10):
        s += str(random.randint(1,10))
    return s


class ForgetpPasswordView(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        from django.core.mail import send_mail, EmailMessage
        username = request.query_params.get('username', None)
        if not User.objects.filter(username=username).exists():
            raise exceptions.NotAcceptable('You are NOT registerd')
        user = User.objects.get(username=username)
        if not user.email:
            raise exceptions.NotAcceptable('Dont have any emails')

        vc = get_verfy_code()
        user.personal_profile.verfy_code = vc
        user.personal_profile.save()
        mail = EmailMessage('verify code', f'Your verify code is {vc}', [user.email])
        print(vc)
        mail.send()
        return Response(data=dict(), status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username', '')
        if not username or not User.objects.filter(username=username).exists() or not data.get('password', ''):
            raise exceptions.NotFound
        user = User.objects.get(username=username)
        if user.personal_profile.verfy_code == data.get('verify_code', 'nn'):
            user.personal_profile.verfy_code = 'n'
            user.personal_profile.save()
            user.set_password(data['password'])
            user.save()
            return Response({'detail': 'password changed'}, status.HTTP_200_OK)
        else:
            raise exceptions.NotAcceptable('verify code is not correct')









