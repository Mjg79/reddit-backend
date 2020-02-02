from rest_framework import exceptions
from rest_framework.authentication import BasicAuthentication
from accounts.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.hashers import PBKDF2PasswordHasher

class Authentication(BasicAuthentication):

    model = User

    def authenticate_credentials(self, userid, password, request=None):

        try:
            user = self.model.objects.get(username=userid)
        except:
            try:
                user = self.model.objects.get(email=userid)
            except:
                raise exceptions.AuthenticationFailed(_('You have not registered'))
        else:
            print(settings.PASSWORD_HASHERS)


        if not user.check_password(password):
            raise exceptions.AuthenticationFailed(_('Invalid username or password.'))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('This user is deactivated!'))

        return user, None