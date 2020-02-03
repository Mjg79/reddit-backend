from rest_framework import serializers
from accounts.models import User
from django.contrib.auth.validators import ASCIIUsernameValidator


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


class AuthorSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']
        read_only_fields = fields

    def get_avatar(self, obj: User):
        return obj.personal_profile.picture.url if obj.personal_profile.picture else ''
