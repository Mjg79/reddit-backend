from rest_framework import serializers
from socials.models import *
from jalali_date import datetime2jalali
from accounts.api.serializers import UserSerializer
from django.contrib.contenttypes.models import ContentType


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username')
    answering_id = serializers.CharField(source='answering.id')
    create_time = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author_name', 'answering_id', 'create_time']
        read_only_fields = fields

    def get_create_time(self, obj: Comment):
        return datetime2jalali(obj.created).strftime('%Y/%m/%d %H:%M') if obj.created else ''


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username')
    channel_id = serializers.CharField(source='channel.id')
    comments = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'author_name', 'channel_id', 'comments', 'create_time']
        read_only_fields = fields

    def get_comments(self, obj: Post):
        return CommentSerializer(instance=obj.comments, many=True).data

    def get_create_time(self, obj: Post):
        return datetime2jalali(obj.created).strftime('%Y/%m/%d %H:%M') if obj.created else ''


class ChannelSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField(required=False)
    admin = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Channel
        fields = ['name', 'authors', 'admin', 'rules', 'avatar']
        read_only_fields = fields

    def get_authors(self, obj: Channel):
        from accounts.api.serializers import AuthorSerializer
        return AuthorSerializer(instance=obj.authors, many=True).data

    def get_admin(self, obj: Channel):
        return UserSerializer(instance=obj.admin).data


class NotificationSerializer(serializers.ModelSerializer):
    For = serializers.SerializerMethodField()
    who_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['situation', 'audience_type', 'For', 'who_name']
        read_only_fields = fields

    def get_For(self, obj: Notification):
        if obj.audience_type == ContentType.objects.get(model='post'):
            data = {'mode':'post'}
        elif obj.audience_type == ContentType.objects.get(model='comment'):
            data = {'model':'comment'}
        else:
            data = {'model':'follow'}
        data['id'] = obj.audience_id
        return data

    def get_who_name(self, obj: Notification):
        return obj.who.first_name + ' ' + obj.who.last_name

