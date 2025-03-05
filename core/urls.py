from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static





urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('transactions/', include('transactions.urls')),
    path('', views.home, name='home'),  # Home page
    path('community/', include('community.urls')),
    path('tokens/', include('tokens.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)