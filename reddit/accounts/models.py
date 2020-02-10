import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import generate_random_username
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from regions.models import City
from regions.abstractModels import TimestampedModel
from djchoices import ChoiceItem, DjangoChoices
from versatileimagefield.fields import VersatileImageField
from django.conf import settings
from django.utils import timezone

__all__ = [
    'User',
    'GenderChoices',
    'Profile'
]


def personal_profile_path(instance, img):
    time = timezone.now()
    path = f'{instance.user.username}/{time.year}/{time.month}/{img}'
    return path


class User(AbstractUser):
    username = models.CharField(
        verbose_name=_('username'),
        max_length=150,
        unique=True,
        default=generate_random_username,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[ASCIIUsernameValidator()],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), db_index=True, blank=True)
    phone = models.CharField(
        verbose_name=_('phone'),
        max_length=15,
        validators=[
            RegexValidator(regex=r'^\d+$', message=_('Phone number should only be comprised of digits.')),
        ],
        db_index=True,
        blank=True,
    )
    city = models.ForeignKey(
        to=City,
        verbose_name=_('city'),
        related_name='users',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    USERNAME_FIELD = 'username'


class GenderChoices(DjangoChoices):
    MALE = ChoiceItem('MALE', _('MALE'))
    FEMALE = ChoiceItem('FEMALE', _('FEMALE'))


class Profile(TimestampedModel):
    user = models.OneToOneField(
        to='accounts.User',
        verbose_name=_('user'),
        related_name='personal_profile',
        on_delete=models.CASCADE
    )
    birth_date = models.DateField(
        verbose_name=_('birth date'),
        blank=True,
        null=True
    )
    bio = models.TextField(null=True, blank=True)
    picture = VersatileImageField(
        verbose_name=_('picture'),
        blank=True,
        upload_to=personal_profile_path,
        max_length=255,
    )
    followed_by = models.ManyToManyField(
        to=User,
        verbose_name=_('followers'),
        related_name='followings_user',
    )
    verfy_code = models.CharField(max_length=11, null=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

