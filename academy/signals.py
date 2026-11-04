from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import User


@receiver(post_delete, sender=User)
def delete_profile_photo(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.storage.delete(instance.photo.name)
