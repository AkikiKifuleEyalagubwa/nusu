from django import template
from users.models import Notification  # Add this import

register = template.Library()

@register.filter
def unread_notifications_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()