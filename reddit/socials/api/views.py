from rest_framework import viewsets, generics, exceptions, status
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsAuthor, IsFollowed, IsAdmin
from rest_framework.request import Request
from rest_framework.response import Response
from accounts.api.auth import Authentication
from django.utils.html import strip_tags
from django.contrib.auth import user_logged_in, user_logged_out
from accounts.models import User
from django.db import transaction
from socials.models import Post, FeedbackChoices
from .serializers import *
from django.utils import timezone
from datetime import timedelta
from django.db.models import *


class HotsView(generics.ListAPIView):
    queryset = Post.objects.none()
    permission_classes = [IsAuthenticated]
    authentication_classes = [Authentication]

    def get(self, request, *args, **kwargs):
        from socials.api.serializers import PostSerializer
        posts = Post.objects.filter(created__gte=timezone.now() - timedelta(days=7)).annotate(
            like=Count('likes', filter=Q(likes__feedback=FeedbackChoices.POSITIVE))
        ).order_by('-like')
        return Response(data=PostSerializer(instance=posts, many=True,context={'request':request}).data, status=status.HTTP_200_OK)


class NewsView(generics.ListAPIView):
    queryset = Post.objects.none()
    permission_classes = [IsAuthenticated]
    authentication_classes = [Authentication]

    def get(self, request, *args, **kwargs):
        from socials.api.serializers import PostSerializer
        return Response(
            data=PostSerializer(instance=Post.objects.all().order_by('-created'), many=True,context={'request':request}).data,
            status=status.HTTP_200_OK
        )


class ActivitiesView(generics.ListAPIView):
    queryset = Post.objects.none()
    permission_classes = [IsAuthenticated]
    authentication_classes = [Authentication]

    def get(self, request, *args, **kwargs):
        post_ids = list(Comment.objects.filter(
            author=request.user, answering=None
        ).values_list('post__id', flat=True).distinct())
        post_ids += list(Comment.objects.filter(
            author=request.user, post=None).values_list('answering__post__id', flat=True).distinct())
        post_ids += list(
            Like.objects.filter(feedbacker=request.user, comment=None).values_list('post__id', flat=True).distinct()
        )
        post_ids += list(
            Like.objects.filter(
                feedbacker=request.user, post=None, comment__answering=None
            ).values_list('comment__post__id', flat=True).distinct()
        )
        ps = Post.objects.filter(Q(author=request.user) | Q(id__in=post_ids))
        return Response(data=PostSerializer(instance=ps, many=True, context={'request':request}).data, status=status.HTTP_200_OK)


class DashboardView(generics.ListAPIView):
    queryset = Post.objects.none()
    permission_classes = [IsAuthenticated]
    authentication_classes = [Authentication]

    def get(self, request, *args, **kwargs):
        f_person_ids = request.user.followings_user.all().values_list('id', flat=True).distinct()
        f_channel_ids = request.user.followings_channel.all().values_list('id', flat=True).distinct()
        return Response(
            data=PostSerializer(instance=Post.objects.filter(
                Q(author__id__in=f_person_ids) | Q(channel__id__in=f_channel_ids)
            ), many=True, context={'request':request}
            ).data,
            status=status.HTTP_200_OK
        )


class PostModelView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAuthor]

    def update(self, request, *args, **kwargs):
        from .serializers import PostModelSerializer
        serializer = PostModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = Post.objects.get(id=kwargs['id'])
        serializer.update(post, serializer.validated_data)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        post = Post.objects.get(kwargs['id'])
        post.delete()
        return Response(dict(), status.HTTP_200_OK)


class PostDetailView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthor]
    serializer_class = PostSerializer

    def create(self, request, *args, **kwargs):
        text = request.data.get('text', '')
        channel_id = request.data.get('channel_id', '')
        image = request.data.get('image', None)
        try:
            channel = Channel.objects.get(id=channel_id)
        except:
            channel = None
        post = Post.objects.create(text=text, channel=channel, image=image, author=request.user)
        serializer = self.get_serializer(instance=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        id = self.request.query_params.get('post_id', None)
        if id:
            return Post.objects.filter(id=id)
        else:
            raise exceptions.NotFound('return id')

    @action(detail=False, methods=['get'])
    def available_channels(self, request):
        user = request.user
        chs = Channel.objects.filter(
            id__in=list(user.channels_author.all().values_list('id', flat=True)) + list(user.channels_admin.all().values_list('id', flat=True))
        )
        channels = []
        for c in chs:
            d = {'name': c.name, 'id': c.id, 'avatar': c.avatar.url if c.avatar else ''}
            channels.append(d)
        return Response(data={'channels': channels}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], permission_classes=[IsFollowed])
    def feedback(self, request):
        from socials.models import Like, FeedbackChoices
        pk = request.data.get('id', 0)
        l = request.query_params.get('like', 0)
        if Like.objects.filter(feedbacker=request.user, post__id=pk).exists():
            like = Like.objects.get(feedbacker=request.user, post__id=pk)
            if l == 0:
                like.feedback = None
            elif l == 1:
                like.feedback = FeedbackChoices.POSITIVE
            else:
                like.feedback = FeedbackChoices.NEGATIVE
            like.save()
        else:
            if l == 0:
                choice = None
            elif l == 1:
                choice = FeedbackChoices.POSITIVE
            else:
                choice = FeedbackChoices.NEGATIVE
            like = Like.objects.create(feedbacker=request.user, feedback=choice, post=Post.objects.get(id=pk))
        return Response({'status': like.feedback}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsFollowed])
    def comment(self, request):
        post = Post.objects.get(id=request.data.get('id', 0))
        comment = Comment.objects.create(author=request.user, post=post, text=request.data.get('text', ''))
        return Response(data={'id': comment.id}, status=status.HTTP_201_CREATED)


class ChannelView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = ChannelModelSerializer

    def update(self, request, *args, **kwargs):
        channel = Channel.objects.get(id=kwargs['id'])
        data = request.data
        if not data.get('authors', None):
            data['authors'] = str(channel.admin_id)
        ser = ChannelModelSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.update(channel, ser.validated_data)
        return Response(ser.data, status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        channel = Channel.objects.get(id=kwargs['id'])
        channel.delete()
        return Response({'detail': 'deleted'}, status.HTTP_200_OK)


class ChanneDetaillView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = ChannelModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ch = serializer.save()
        return Response(data={'channel_id': ch.id}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsAdmin])
    def potential_authors(self, request, pk):
        from accounts.api.serializers import AuthorSerializer
        channel = Channel.objects.get(id=pk)
        return Response(
            data=AuthorSerializer(instance=channel.followed_by.all(), many=True).data,
            status=status.HTTP_200_OK
        )

    def get_queryset(self):
        pk = self.request.query_params.get('id', None)
        if pk:
            return Channel.objects.filter(id=pk)
        return []


class NotifView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.none()

    def retrieve(self, request, *args, **kwargs):
        lst = request.user.notifs.filter(seen=False)
        return Response(data=self.get_serializer(instance=lst, many=True).data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        lst = request.user.notifs.filter(seen=False)
        for n in lst:
            n.seen = True
            n.save()
        return Response(dict(), status.HTTP_200_OK)


class CommentView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        try:
            pk = self.request.query_params.get('id', None)
            if pk:
                return Comment.objects.get(id=pk)
        except:
            return Comment.objects.none()

    @action(detail=False, methods=['put'], permission_classes=[IsFollowed])
    def feedback(self, request):
        pk = request.data.get('id', 0)
        l = request.query_params.get('like', 0)
        if Like.objects.filter(feedbacker=request.user, comment_id=pk).exists():
            like = Like.objects.get(feedbacker=request.user, comment_id=pk)
            if l == 0:
                like.feedback = None
            elif l == 1:
                like.feedback = FeedbackChoices.POSITIVE
            else:
                like.feedback = FeedbackChoices.NEGATIVE
            like.save()
        else:
            if l == 0:
                choice = None
            elif l == 1:
                choice = FeedbackChoices.POSITIVE
            else:
                choice = FeedbackChoices.NEGATIVE
            like = Like.objects.create(feedbacker=request.user, feedback=choice, comment=Comment.objects.get(id=pk))
        return Response({'status': like.feedback}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsFollowed])
    def comment(self, request):
        comment = Comment.objects.get(id=request.data.get('id', ''))
        c = Comment.objects.create(author=request.user, answering=comment, text=request.data.get('text', ''))
        return Response(data={'id': c.id}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def answers(self, request, pk):
        comment = Comment.objects.get(id=pk)
        return Response(
            data=CommentSerializer(instance=comment.answers.all(), many=True).data,
            status=status.HTTP_200_OK
        )


class SearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from accounts.api.serializers import AuthorSerializer

        q = request.query_params.get('q', '')
        posts = Post.objects.filter(text__icontains=q)
        channels = Channel.objects.filter(name__icontains=q)
        users = User.objects.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )
        data = {
            'channels': ChannelSerializer(instance=channels, many=True).data,
            'users': AuthorSerializer(instance=users, many=True).data,
            'posts': PostSerilaizerLite(instance=posts, many=True).data
        }
        return Response(data=data, status=status.HTTP_200_OK)

