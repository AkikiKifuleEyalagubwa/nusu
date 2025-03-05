from django import template
from django.utils.timesince import timesince
from ..models import Tweet

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    return value * arg

@register.filter
def is_retweeted_by(tweet, user):
    """Check if the tweet is retweeted by the given user (safe for anonymous)."""
    if not user.is_authenticated:
        return False
    return tweet.retweets.filter(user=user).exists()

@register.filter
def time_short(value):
    """Formats time as short abbreviation (e.g. 2h, 15m, 3d)"""
    time_str = timesince(value).split(',')[0].strip()
    if 'minute' in time_str:
        return time_str.replace(' minutes', 'm').replace(' minute', 'm')
    if 'hour' in time_str:
        return time_str.replace(' hours', 'h').replace(' hour', 'h')
    if 'day' in time_str:
        return time_str.replace(' days', 'd').replace(' day', 'd')
    if 'week' in time_str:
        return time_str.replace(' weeks', 'w').replace(' week', 'w')
    return time_str
    

@register.filter
def starts_with(value, arg):
    return value.startswith(arg)