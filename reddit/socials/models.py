import os
from django.db import models
from regions.abstractModels import TimestampedModel, ActivatedModel
from djchoices import DjangoChoices, ChoiceItem
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from versatileimagefield.fields import VersatileImageField


__all__=[
    'Channel',
    'Post',
    'Comment',
    'FeedbackChoices',
    'Like',
    'NotifSituations',
    'Notification'
]


def channel_avatar_path(instance):
    return os.path.join(instance.name)


def post_image_path(instance):
    return os.path.join(instance.author.username + 'Post' + instance.author.posts.count())


class Channel(TimestampedModel, ActivatedModel):
    name = models.CharField(
        max_length=30,
        unique=True,
    )
    admin = models.ForeignKey(
        to='accounts.User',
        related_name='channels_admin',
        verbose_name='admin',
        on_delete=models.CASCADE
    )
    authors = models.ManyToManyField(
        to='accounts.User',
        related_name='channels_author',
        verbose_name='authors',
    )
    followed_by = models.ManyToManyField(
        to='accounts.User',
        related_name='followings_channel',
        verbose_name='followers',
    )
    rules = models.TextField(
        blank=True,
        help_text='rules of this channel'
    )
    avatar = VersatileImageField(
        verbose_name='avatar',
        blank=True,
        upload_to=channel_avatar_path,
        max_length=255,
    )


class Post(TimestampedModel, ActivatedModel):
    text = models.TextField()
    author = models.ForeignKey(
        to='accounts.User',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    channel = models.ForeignKey(
        to=Channel,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    image = VersatileImageField(
        verbose_name='image',
        blank=True,
        upload_to=post_image_path,
        max_length=255,
    )


class Comment(TimestampedModel, ActivatedModel):
    author = models.ForeignKey(
        to='accounts.User',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    answering = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='answers',
        null=True
    )


class FeedbackChoices(DjangoChoices):
    POSITIVE = ChoiceItem('POSITIVE', 'POSITIVE')
    NEGATIVE = ChoiceItem('NEGATIVE', 'NEGATIVE')


class Like(TimestampedModel, ActivatedModel):
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='likes',
        null=True
    )
    comment = models.ForeignKey(
        to=Comment,
        on_delete=models.CASCADE,
        related_name='likes',
        null=True
    )
    feedbacker = models.ForeignKey(
        to='accounts.User',
        on_delete=models.CASCADE,
        related_name='likes_or_dislikes'
    )
    feedback = models.CharField(
        max_length=32,
        choices=FeedbackChoices.choices,
        validators=[FeedbackChoices.validator],
    )


class NotifSituations(DjangoChoices):
    FOLLOWED = ChoiceItem('FOLLOWED', 'FOLLOWED')
    COMMENT_ON_COMMENT = ChoiceItem('COMMENT_ON_COMMENT', 'Comment on Comment')
    LIKE_ON_COMMENT = ChoiceItem('LIKE_ON_COMMENT', 'Like on Comment')
    LIKE_ON_POST = ChoiceItem('LIKE_ON_POST', 'Like on Post')
    COMMENT_ON_POST = ChoiceItem('COMMENT_ON_POST', 'Comment on Post')


class Notification(TimestampedModel):
    for_user = models.ForeignKey(
        to='accounts.User',
        on_delete=models.CASCADE,
        related_name='notifs',
    )
    situation = models.CharField(
        max_length=32,
        choices=NotifSituations.choices,
        validators=[NotifSituations.validator],
    )
    who = models.ForeignKey(
        to='accounts.User',
        on_delete=models.CASCADE,
        related_name='notifs_sent',
        null=True
    )
    audience_type = models.ForeignKey(
        to=ContentType,
        verbose_name='audience type',
        on_delete=models.CASCADE,
    )
    audience_id = models.UUIDField('audience id')
    audience_object = GenericForeignKey('audience_type', 'audience_id')
