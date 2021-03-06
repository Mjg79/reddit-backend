from rest_framework import serializers
from socials.models import *
from jalali_date import datetime2jalali
from django.contrib.contenttypes.models import ContentType


class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()
    can_reply = serializers.SerializerMethodField()
    no_feedbacks = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'create_time', 'can_reply', 'no_feedbacks', 'like', 'image']
        read_only_fields = fields

    def get_image(self, obj: Comment):
        return obj.image.url if obj.image else ''

    def get_no_feedbacks(self, obj: Comment):
        return {
            'likes': obj.likes.filter(feedback=FeedbackChoices.POSITIVE).count(),
            'dislikes': obj.likes.filter(feedback=FeedbackChoices.NEGATIVE).count()
        }

    def get_like(self, obj: Comment):
        if not obj.likes.filter(feedbacker=self.context['request'].user).exists():
            return 0
        elif obj.likes.filter(feedbacker=self.context['request'].user, feedback=FeedbackChoices.POSITIVE).exists():
            return 1
        else:
            return -1

    def get_author(self, obj: Comment):
        return {
            'name': obj.author.username,
            'avatar': obj.author.personal_profile.picture.url if obj.author.personal_profile.picture else '',
            'id': obj.author.id
        }

    def get_can_reply(self, obj: Comment):
        return False

    def get_create_time(self, obj: Comment):
        return datetime2jalali(obj.created).strftime('%Y/%m/%d %H:%M') if obj.created else ''


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()
    can_reply = serializers.SerializerMethodField()
    no_feedbacks = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'create_time', 'answers', 'can_reply', 'no_feedbacks', 'like', 'image']
        read_only_fields = fields

    def get_image(self, obj: Comment):
        return obj.image.url if obj.image else ''

    def get_no_feedbacks(self, obj: Comment):
        return {
            'likes': obj.likes.filter(feedback=FeedbackChoices.POSITIVE).count(),
            'dislikes': obj.likes.filter(feedback=FeedbackChoices.NEGATIVE).count()
        }

    def get_like(self, obj: Comment):
        if not obj.likes.filter(feedbacker=self.context['request'].user).exists():
            return 0
        elif obj.likes.filter(feedbacker=self.context['request'].user, feedback=FeedbackChoices.POSITIVE).exists():
            return 1
        else:
            return -1

    def get_author(self, obj: Comment):
        return {
            'name': obj.author.username,
            'avatar': obj.author.personal_profile.picture.url if obj.author.personal_profile.picture else '',
            'id': obj.author.id
        }

    def get_can_reply(self, obj: Comment):
        return True

    def get_create_time(self, obj: Comment):
        return datetime2jalali(obj.created).strftime('%Y/%m/%d %H:%M') if obj.created else ''

    def get_answers(self, obj: Comment):
        data = []
        if obj.answers.count():
            return AnswerSerializer(instance=obj.answers.all(), many=True, context=self.context).data
        return data


class PostModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    channel = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()
    no_feedbacks = serializers.SerializerMethodField()
    no_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'author', 'channel', 'comments', 'create_time', 'like',
                  'no_feedbacks', 'image', 'no_comments'
                  ]
        read_only_fields = fields

    def get_no_comments(self, obj: Post):
        return obj.comments.count()

    def get_comments(self, obj: Post):
        return CommentSerializer(instance=obj.comments, many=True, context=self.context).data

    def get_create_time(self, obj: Post):
        return datetime2jalali(obj.created).strftime('%Y/%m/%d %H:%M') if obj.created else ''

    def get_author(self, obj: Post):
        from accounts.api.serializers import AuthorSerializer
        return AuthorSerializer(instance=obj.author, context=self.context).data

    def get_like(self, obj: Post):
        like = Like.objects.filter(feedbacker=self.context['request'].user, post=obj)
        if like.filter(feedback=FeedbackChoices.POSITIVE).exists():
            return 1
        elif like.filter(feedback=FeedbackChoices.NEGATIVE).exists():
            return -1
        else:
            return 0

    def get_no_feedbacks(self, obj: Post):
        return {
            'likes':Like.objects.filter(post=obj, feedback=FeedbackChoices.POSITIVE).count(),
            'dislikes':Like.objects.filter(post=obj, feedback=FeedbackChoices.NEGATIVE).count()
        }

    def get_channel(self, obj: Post):
        return ChannelSerializer(instance=obj.channel, context=self.context).data if obj.channel else {}


class PostSerilaizerLite(serializers.ModelSerializer):
    no_feedbacks = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'author', 'no_feedbacks', 'like']

    def get_like(self, obj: Post):
        like = Like.objects.filter(feedbacker=self.context['request'].user, post=obj)
        if like.exists():
            return 1 if like.filter(feedback=FeedbackChoices.POSITIVE).exists() else -1
        else:
            return 0

    def get_no_feedbacks(self, obj: Post):
        return {
            'likes': Like.objects.filter(post=obj, feedback=FeedbackChoices.POSITIVE).count(),
            'dislikes': Like.objects.filter(post=obj, feedback=FeedbackChoices.NEGATIVE).count()
        }

    def get_author(self, obj: Post):
        from accounts.api.serializers import AuthorSerializer
        return AuthorSerializer(instance=obj.author, context=self.context).data


class ChannelSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField(required=False)
    admin = serializers.SerializerMethodField(required=False)
    no_followers = serializers.SerializerMethodField(required=False)
    no_posts = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Channel
        fields = ['id', 'name', 'authors', 'admin', 'rules', 'avatar', 'no_followers', 'no_posts']
        read_only_fields = fields

    def get_authors(self, obj: Channel):
        from accounts.api.serializers import AuthorSerializer
        return AuthorSerializer(instance=obj.authors, many=True, context=self.context).data

    def get_admin(self, obj: Channel):
        from accounts.api.serializers import UserSerializer
        return UserSerializer(instance=obj.admin).data

    def get_no_followers(self, obj: Channel):
        return obj.followed_by.count()

    def get_no_posts(self, obj: Channel):
        return Post.objects.filter(channel=obj).count()


class ChannelModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'name', 'rules', 'authors', 'avatar', 'admin']


class ChannelDetailSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField(required=False)
    user_admin = serializers.SerializerMethodField(required=False)
    no_followers = serializers.SerializerMethodField(required=False)
    no_posts = serializers.SerializerMethodField(required=False)
    posts = serializers.SerializerMethodField(required=False)
    follow = serializers.SerializerMethodField(required=False)
    avatar = serializers.ImageField('avatar')

    class Meta:
        model = Channel
        fields = [
            'id', 'name', 'authors', 'admin', 'rules', 'avatar', 'user_admin',
            'no_followers', 'no_posts', 'posts', 'follow'
        ]
        read_only_fields = fields

    def get_authors(self, obj: Channel):
        from accounts.api.serializers import AuthorSerializer
        return AuthorSerializer(instance=obj.authors, many=True, context=self.context).data

    def get_user_admin(self, obj: Channel):
        from accounts.api.serializers import UserSerializer
        return UserSerializer(instance=obj.admin).data

    def get_no_followers(self, obj: Channel):
        return obj.followed_by.count()

    def get_no_posts(self, obj: Channel):
        return Post.objects.filter(channel=obj).count()

    def get_posts(self, obj: Channel):
        return PostSerilaizerLite(instance=obj.posts.all(), many=True, context=self.context).data

    def get_follow(self, obj: Channel):
        return self.context['request'].user in obj.followed_by.all()


class NotificationSerializer(serializers.ModelSerializer):
    For = serializers.SerializerMethodField()
    who = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['situation', 'audience_type', 'For', 'who']
        read_only_fields = fields

    def get_For(self, obj: Notification):
        if obj.audience_type == ContentType.objects.get(model='post'):
            data = {'model': 'post'}
        elif obj.audience_type == ContentType.objects.get(model='comment'):
            data = {'model': 'comment'}
        else:
            data = {'model': 'follow'}
        data['id'] = obj.audience_id
        return data

    def get_who(self, obj: Notification):
        return {
            'name': obj.who.username,
            'id': obj.who.id,
            'avatar': obj.who.personal_profile.picture.url if obj.who.personal_profile.picture else ''
        }

