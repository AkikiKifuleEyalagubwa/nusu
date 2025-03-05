from django.contrib import admin
from .models import Streak

@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_deposit_days', 'days_on_network', 'current_badge')
    list_filter = ('current_badge',)
    search_fields = ('user__username',)
    readonly_fields = ('total_deposit_days', 'days_on_network', 'last_deposit_date')