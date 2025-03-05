from django.db import models
from users.models import CustomUser

class Streak(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    total_deposit_days = models.PositiveIntegerField(default=0)
    days_on_network = models.PositiveIntegerField(default=0)
    last_deposit_date = models.DateField(null=True, blank=True)
    current_badge = models.CharField(max_length=10, blank=True)  # Platinum, Gold, etc.

    def __str__(self):
        return f"{self.user.username}'s Streak: {self.total_deposit_days} days"