from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io


def create_default_profile_picture(user):
    # Create a blank image
    img = Image.new('RGB', (200, 200), color=(73, 109, 137))  # Background color
    draw = ImageDraw.Draw(img)

    # Use the first letter of the username
    initial = user.username[0].upper() if user.username else 'U'

    try:
        font = ImageFont.truetype("arial.ttf", 100)  # Adjust font size
    except:
        font = ImageFont.load_default()

    # Calculate text position
    text_width, text_height = draw.textsize(initial, font)
    x = (200 - text_width) // 2
    y = (200 - text_height) // 2

    # Draw the initial
    draw.text((x, y), initial, font=font, fill=(255, 255, 255))  # White text

    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())

# Custom User Model
class CustomUser(AbstractUser):
    is_agent = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default.png'  # Default profile picture
    )
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='following')
    verified = models.BooleanField(default=False)
    ugx_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    BADGE_CHOICES = [
        ('none', 'No Badge'),  # Add 'none' as the default option
        ('bronze', 'Bronze Member'),
        ('silver', 'Silver Member'),
        ('gold', 'Gold Member'),
        ('platinum', 'Platinum Admin')
    ]
    badge = models.CharField(max_length=20, choices=BADGE_CHOICES, default='none')
    days_active = models.PositiveIntegerField(default=0)
    days_deposited = models.PositiveIntegerField(default=0)

    def get_badge_icon(self):
        """Returns the badge icon class based on the badge level."""
        badge_icons = {
            'none': 'bi-award',  # Default icon for no badge
            'bronze': 'bi-award',
            'silver': 'bi-award-fill',
            'gold': 'bi-trophy',
            'platinum': 'bi-patch-check-fill'
        }
        return badge_icons.get(self.badge, 'bi-award')

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_ugx_balance(self):
        from tokens.models import TokenRate
        rate = TokenRate.objects.last()
        if rate:
            return self.token_balance * rate.rate
        return 0  # Or handle this case appropriately

# Notification Model
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    transaction = models.ForeignKey('transactions.Transaction', on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

# Signal to create a user profile when a new user is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        
        # Save a default profile picture if none exists
        if not profile.profile_picture:
            profile.profile_picture.save(
                f'{instance.username}_profile.png',
                create_default_profile_picture()
            )
        profile.save()