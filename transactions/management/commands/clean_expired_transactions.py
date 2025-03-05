# transactions/management/commands/clean_expired_transactions.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from transactions.models import Transaction

class Command(BaseCommand):
    help = 'Marks expired withdrawal requests as expired'

    def handle(self, *args, **options):
        now = timezone.now()
        expired = Transaction.objects.filter(
            status='pending',
            expiry__lt=now
        ).update(status='expired')
        
        self.stdout.write(self.style.SUCCESS(
            f'Marked {expired} transactions as expired'
        ))