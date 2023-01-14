import json

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from .models import User, UserActivityLog
from notification.models import BroadCastNotificationModel


def get_request_value():
    import inspect
    for frame_record in inspect.stack():
        if frame_record[3]=='get_response':
            request = frame_record[0].f_locals['request'].user
            break
        else:
            request = None
    return request

@receiver(pre_save, sender = User)
def username_create(sender, instance, *args, **kwargs):
    if instance.email:
        instance.username = instance.email


@receiver(post_save, sender=User)
def create_Activity_Log(sender, instance, created, *args, **kwargs):
    model_name = instance.__class__.__name__

    if not get_request_value() == None:
        action_by = f'{get_request_value().first_name} {get_request_value().last_name}'
        if created:
            action = f"{model_name} Created"
            description = f"A {model_name}  {instance} 'Was Created' By {action_by} "
    action = f"{model_name} Created"
    description = f"A {model_name}  {instance} 'Was Created' By {instance} "

    UserActivityLog.objects.create(
                action=action,
                action_by=get_request_value(),
                description=description,
                action_date=timezone.now(),
                )


@receiver(post_save, sender=BroadCastNotificationModel)
def notification_handler(sender, instance,created, *args,**kwargs):
    if created:
        scheduled, created = CrontabSchedule.objects.get_or_create(hour=instance.broadcast_on.hour, minute=instance.broadcast_on.minute, day_of_month=instance.broadcast_on.day, month_of_year =instance.broadcast_on.month)
        task = PeriodicTask.objects.create(crontab=scheduled, name="broadcast-notification-" + str(instance.id), task="notification.tasks.broadcast_notification", args=json.dumps((instance.id,)))
