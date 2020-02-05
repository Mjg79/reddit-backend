from rest_framework import permissions
from socials.models import Channel, Post, Comment


class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        channel_id = request.data.get('channel_id', None)
        if not channel_id:
            return True
        channel = Channel.objects.get(id=channel_id)
        return request.user in channel.authors.all() or request.user == channel.admin


class IsFollowed(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            obj = Post.objects.get(id=request.data['id'])
        except:
            obj = Comment.objects.get(id=request.data['id'])
        if isinstance(obj, Comment):
            if obj.post:
                obj = obj.post
            else:
                obj = obj.answering.post
        if obj.channel:
            return request.user in obj.channel.followed_by.all()
        else:
            return request.user in obj.author.personal_profile.followed_by.all()
