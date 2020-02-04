from rest_framework import permissions
from socials.models import Channel


class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        channel_id = request.data.get('channel_id', None)
        if not channel_id:
            return True
        channel = Channel.objects.get(id=channel_id)
        return request.user in channel.authors.all() or request.user == channel.admin
