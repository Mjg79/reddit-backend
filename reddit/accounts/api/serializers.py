from rest_framework import serializers
from reddit.accounts.models import User

class LoginSerializer(serializers.ModelSerializer):


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'email']
        read_only_fields = ['id', 'phone']
