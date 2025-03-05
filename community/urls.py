from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('tweet/<int:tweet_id>/', views.tweet_detail, name='tweet_detail'),
    path('tweet/<int:tweet_id>/like/', views.toggle_like, name='toggle_like'),
    path('tweet/<int:tweet_id>/retweet/', views.retweet_tweet, name='retweet_tweet'),
    path('tweet/<int:tweet_id>/undo_retweet/', views.undo_retweet, name='undo_retweet'),
    path('tweet/<int:tweet_id>/quote/', views.quote_retweet, name='quote_retweet'),
    path('tweet/<int:tweet_id>/reply/', views.reply_tweet, name='reply_tweet'),
    path('compose/<int:tweet_id>/', views.create_tweet, name='create_tweet'),
    path('compose/', views.create_tweet, name='create_tweet'),
    path('tweet/<int:tweet_id>/delete/', views.delete_tweet, name='delete_tweet'),
    path('thread/<int:tweet_id>/', views.thread_detail, name='thread_detail'),
    path('search/', views.search_results, name='search'),
    path('search/autocomplete/', views.search_autocomplete, name='autocomplete'),
    path('trending/', views.trending, name='trending'),
]

