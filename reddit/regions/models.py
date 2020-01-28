from reddit.regions.abstractModels import TimestampedModel, ActivatedModel
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Country(TimestampedModel, ActivatedModel):
    name = models.CharField(verbose_name=_('name'), max_length=64)

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('country')
        ordering = ['-created']

    def __str__(self):
        return self.name


class City(TimestampedModel, ActivatedModel):
    name = models.CharField(verbose_name=_('name'), max_length=64)
    country = models.ForeignKey(
        to=Country,
        verbose_name=_('country'),
        related_name='cities',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')

    def __str__(self):
        return self.name
