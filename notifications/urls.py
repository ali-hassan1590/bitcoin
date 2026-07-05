from django.urls import path
from .views import NotificationListView, MarkNotificationReadView

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("notifications/<uuid:pk>/read/", MarkNotificationReadView.as_view(), name="notification-read"),
]