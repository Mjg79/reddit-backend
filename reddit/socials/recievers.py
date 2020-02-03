from django.dispatch import receiver
from django.db.models.signals import post_save
from  socials.models import Like, Comment, Notification, NotifSituations
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Like, dispatch_uid='socials.notif_after_like')
def notif_after_like(sender, instance: Like, created: bool, **kwargs):
    if instance.post is not None:
        ctype = ContentType.objects.get(model='post')
        cid = instance.post.id
        Notification.objects.create(
            for_user=instance.post.author, situation=NotifSituations.LIKE_ON_POST,
            audience_id=cid, audience_type=ctype, who=instance.feedbacker
        )
    else:
        ctype = ContentType.objects.get(model='comment')
        cid = instance.comment.id
        Notification.objects.create(
            for_user=instance.comment.author, situation=NotifSituations.LIKE_ON_COMMENT,
            audience_id=cid, audience_type=ctype, who=instance.feedbacker
        )


@receiver(post_save, sender=Comment, dispatch_uid='socials.notif_after_comment')
def notif_after_comment(sender, instance: Comment, created: bool, **kwargs):
    if instance.answering is not None:
        ctype = ContentType.objects.get(model='comment')
        cid = instance.answering.id
        Notification.objects.create(
            for_user=instance.answering.author, situation=NotifSituations.COMMENT_ON_COMMENT,
            audience_id=cid, audience_type=ctype, who=instance.author
        )
    else:
        ctype = ContentType.objects.get(model='post')
        cid = instance.post.id
        Notification.objects.create(
            for_user=instance.post.author, situation=NotifSituations.COMMENT_ON_POST,
            audience_id=cid, audience_type=ctype, who=instance.author
        )
