from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task(bind=True)
def test_func(self):
    return "HAhah"