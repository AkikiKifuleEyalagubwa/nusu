from django.contrib import admin
from .models import TokenRate, TokenAllocation

@admin.register(TokenRate)
class TokenRateAdmin(admin.ModelAdmin):
    list_display = ('rate', 'effective_date', 'set_by')
    list_filter = ('effective_date',)
    search_fields = ('set_by__username',)
    readonly_fields = ('effective_date',)

@admin.register(TokenAllocation)
class TokenAllocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'allocated_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'allocated_by__username')
    readonly_fields = ('created_at',)