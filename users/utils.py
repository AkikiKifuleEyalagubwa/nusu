# users/utils.py - Update BadgeManager
from django.db.models import Sum
from transactions.models import Transaction 
from django.utils import timezone


class BadgeManager:
    @staticmethod
    def calculate_badge(profile):
        if profile.user.is_superuser:
            return 'platinum'
        
        # Get total deposits (not just days)
        deposits = Transaction.objects.filter(  # Now this will work
            user=profile.user,
            transaction_type='deposit'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get account age in days
        account_age = (timezone.now() - profile.user.date_joined).days
        activity_ratio = deposits / account_age if account_age > 0 else 0
        
        # Badge thresholds
        if deposits >= 1000 and activity_ratio >= 0.9:
            return 'platinum'
        if deposits >= 500 and activity_ratio >= 0.7:
            return 'gold'
        if deposits >= 100 and activity_ratio >= 0.5:
            return 'silver'
        if deposits >= 50:
            return 'bronze'
            
        return 'none'