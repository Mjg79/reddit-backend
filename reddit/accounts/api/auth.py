from rest_framework import exceptions
from rest_framework.authentication import BasicAuthentication
from reddit.accounts.models import User


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

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed(_('Invalid username or password.'))

        try:
            sec_user, is_new = User.objects.get_or_create(email=userid)
        except:
            sec_user, is_new = User.objects.get_or_create(username=userid)

            if is_new:
                user.set_unusable_password()

            if not user:
                user = sec_user
                user.save()

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('This user is deactivated!'))

        return user, None