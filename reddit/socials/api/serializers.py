from rest_framework import serializers
from socials.models import *
from jalali_date import datetime2jalali


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username')
    answering_id = serializers.CharField(source='answering.id')
    created_time = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author_name', 'answering_id']
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
        fields = ['id', 'text', 'author_name', 'channel_id', 'comments', 'created_time']
        read_only_fields = fields

    def get_comments(self, obj: Post):
        return CommentSerializer(instance=obj.comments, many=True).data

    def get_create_time(self, obj: Post):
        return datetime2jalali(obj.created).strftime('%Y/%m/%d %H:%M') if obj.created else ''


