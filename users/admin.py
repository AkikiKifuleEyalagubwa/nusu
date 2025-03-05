# users/admin.py
from django.contrib import admin
from .models import CustomUser, UserProfile



# Unregister if already registered
if UserProfile in admin.site._registry:
    admin.site.unregister(UserProfile)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_balance', 'get_ugx_balance', 'verified', 'badge')
    list_filter = ('verified', 'badge')
    search_fields = ('user__username',)
    list_editable = ('verified', 'badge')

    def get_ugx_balance(self, obj):
        return obj.get_ugx_balance()
    get_ugx_balance.short_description = 'UGX Balance'
    get_ugx_balance.admin_order_field = 'token_balance'  # Allow sorting by token balance


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_agent', 'is_verified')
    list_filter = ('is_agent', 'is_verified')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 
                      'is_agent', 'is_verified')
        }),
    )