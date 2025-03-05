# community/admin.py
from django.contrib import admin
from .models import Tweet  # Replace old imports

admin.site.register(Tweet)