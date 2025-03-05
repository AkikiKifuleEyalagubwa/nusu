# core/context_processors.py
from users.models import Notification
from community.models import Tweet  # Import the Tweet model

def notifications(request):
    context = {
        'unread_notifications': [],
        'unread_notifications_count': 0,
        'is_retweeted_by_user': lambda tweet: False  # Default value for anonymous users
    }

    if request.user.is_authenticated:
        context.update({
            'unread_notifications': request.user.notifications.filter(is_read=False).order_by('-created_at')[:5],
            'unread_notifications_count': request.user.notifications.filter(is_read=False).count(),
            'is_retweeted_by_user': lambda tweet: tweet.is_retweeted_by(request.user)  # Add this line
        })

    return context