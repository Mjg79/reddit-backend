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
from socials.models import Post
from .serializers import *


class DashboardView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [Authentication]

    def get(self, request, *args, **kwargs):

        return Response(data={'ez':'ez'}, status=status.HTTP_200_OK)


class PostView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    # @action()
    # def get_channels(self):

    def create(self, request, *args, **kwargs):
        text = request.data.get('caption', '')
        channel_id = request.data.get('channel_id', '')
        post = Post.objects.create(text=text, channel=Channel.objects.get(id=channel_id), author=request.user)
        serializer = self.get_serializer(instance=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        id = self.query_params.get('post_id', None)
        if id:
            return Post.objects.get(id=id)
        else:
            raise exceptions.NotFound('return id')
