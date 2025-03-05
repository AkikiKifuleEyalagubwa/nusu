from django.contrib import admin
from .models import Transaction, WithdrawalRequest

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'agent', 
        'amount', 
        'transaction_type', 
        'timestamp'
    ]
    list_filter = [
        'transaction_type', 
        'timestamp'
    ]

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'amount', 
        'status', 
        'expiry', 
        'created_at'
    ]
    list_filter = [
        'status', 
        'expiry'
    ]