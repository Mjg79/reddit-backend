from django.db import models
from django.db.models import QuerySet


class TimestampedModel(models.Model):
    """Timestamp mixin

    This mixin adds a timestamp to model for create and update events
    """
    created = models.DateTimeField('created', auto_now_add=True)
    updated = models.DateTimeField('updated', auto_now=True)

    class Meta:
        abstract = True


class ActivatedModelManager(models.Manager):
    @property
    def actives(self) -> QuerySet:
        return self.get_queryset().filter(is_active=True)


class ActivatedModel(models.Model):
    """Active objects mixin

    This mixin add a is_active field to the model
    which indicated the model active status.
    It also adds a queryset to support
    getting only active objects.
    """
    is_active = models.BooleanField(
        'active',
        default=True,
        db_index=True
    )

    objects = ActivatedModelManager()

    class Meta:
        abstract = True


