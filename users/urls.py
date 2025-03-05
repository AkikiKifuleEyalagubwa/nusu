from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
  path('admin-balances/', views.admin_balances, name='admin_balances'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),  # Add this line
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
   path('create-agent/', views.create_agent, name='create_agent'),
    path('send-tokens/', views.send_tokens, name='send_tokens'),
    path('transaction/<int:tx_id>/receipt/', views.transaction_receipt, name='transaction_receipt'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', 
         views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/<int:notification_id>/delete/', 
         views.delete_notification, name='delete_notification'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('assign-badge/', views.assign_badge, name='assign_badge'),  # Add this line
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
  
]








    
    
