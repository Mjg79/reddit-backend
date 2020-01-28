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
        fields = ['id', 'phone', 'first_name', 'last_name', 'email', 'username', 'password']
        read_only_fields = ['id', 'phone']
