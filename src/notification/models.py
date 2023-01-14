from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User


# Create your models here.
class BroadCastNotificationModel(models.Model):
    message = models.TextField()
    broadcast_on = models.DateTimeField()
    sent = models.BooleanField(default=False)
    to_user = models.ForeignKey(User, verbose_name=_("Broadcasted To"), on_delete=models.CASCADE, related_name="broadcasted_to")

    class Meta:
        ordering = ["-broadcast_on"]
