from rest_framework import serializers
from socials.models import *
from jalali_date import datetime2jalali
from accounts.api.serializers import AuthorSerializer, UserSerializer


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
        return AuthorSerializer(instance=obj.authors, many=True).data

    def get_admin(self, obj: Channel):
        return UserSerializer(instance=obj.admin)

