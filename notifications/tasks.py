from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


@shared_task
def send_order_notification(user_id, message):
    """
    Runs in the background — the API response doesn't wait for this.
    """
    Notification.objects.create(
        user_id=user_id,
        notification_type=Notification.NotificationType.ORDER_EXECUTED,
        message=message,
    )