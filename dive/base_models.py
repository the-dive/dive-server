from django.contrib.auth.models import User
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        related_name='%(class)s_created',
        on_delete=models.CASCADE,
    )
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        User,
        related_name='%(class)s_modified',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class NamedModelMixin(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        return '-- No Name --'

    class Meta:
        abstract = True
