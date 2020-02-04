from rest_framework import serializers
from accounts.models import User, Profile
from django.contrib.auth.validators import ASCIIUsernameValidator
from socials.api.serializers import ChannelSerializer
from socials.models import Channel


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        validators=[ASCIIUsernameValidator()]
    )
    password = serializers.CharField(max_length=20)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'email', 'username']
        read_only_fields = ['id', 'phone']


class ProfileSerializer(serializers.ModelSerializer):
    no_followings = serializers.SerializerMethodField(required=False)
    no_followers = serializers.SerializerMethodField(required=False)
    no_posts = serializers.SerializerMethodField(required=False)
    channels = serializers.SerializerMethodField(required=False)
    username = serializers.CharField(source='user.username')
    follow = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'birth_date', 'no_followings', 'no_followers',
            'no_posts', 'channels', 'bio', 'picture', 'follow'
        ]

    def get_no_followers(self, obj: Profile):
        return obj.followed_by.count()

    def get_no_followings(self, obj: Profile):
        return obj.user.followings_channel.count() + \
               obj.user.followings_user.all().values_list('user', flat=True).distinct().count()

    def get_no_posts(self, obj: Profile):
        return obj.user.posts.count()

    def get_channels(self, obj: Profile):
        chs = Channel.objects.filter(
            id__in=list(obj.user.channels_author.all().values_list('id', flat=True)) + list(obj.user.channels_admin.all().values_list('id', flat=True))
        )
        return ChannelSerializer(instance=chs, many=True).data

    def get_follow(self, obj: User):
        user = self.context['request'].get('user', None)
        if not user:
            return False
        return user in obj.personal_profile.followed_by.all()


class AuthorSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    follow = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'follow']
        read_only_fields = fields

    def get_avatar(self, obj: User):
        return obj.personal_profile.picture.url if obj.personal_profile.picture else ''

    def get_follow(self, obj: User):
        user = self.context.get('user', None)
        if not user:
            return False
        return user in obj.personal_profile.followed_by.all()
