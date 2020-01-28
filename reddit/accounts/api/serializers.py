from rest_framework import serializers
from accounts.models import User
from django.contrib.auth.validators import ASCIIUsernameValidator


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[ASCIIUsernameValidator()]
    )
    password = serializers.CharField(max_length=20)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'email', 'username']
        read_only_fields = ['id', 'phone']
