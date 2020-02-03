from rest_framework import serializers
from socials.models import *


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username')
    answering_id = serializers.CharField(source='answering.id')

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author_name', 'answering_id']
        read_only_fields = fields


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username')
    channel_name = serializers.CharField(source='channel.name')
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'author_name', 'channel_name', 'comments']
        read_only_fields = fields

    def get_comments(self, obj: Post):
        return CommentSerializer(instance=obj.comments, many=True).data

