from rest_framework import viewsets, generics, exceptions, status
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from django.contrib.auth import user_logged_in, user_logged_out
from reddit.accounts.models import User

from reddit.accounts.api  import 

class LoginView(generics.CreateAPIView):

    """Login View

    This view is used to initiate and validate user provided `nonce` and `code`.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'login'
    queryset = User.objects.none()
    serializer_class = LoginSerializer
