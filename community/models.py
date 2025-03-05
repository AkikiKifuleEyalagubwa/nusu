import re
from django.db import models
from django.utils import timezone
from users.models import CustomUser

class Tweet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(max_length=280)
    image = models.ImageField(upload_to='tweets/images/', blank=True, null=True)
    video = models.FileField(upload_to='tweets/videos/', blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    retweet = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='retweets')
    quote = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='quotes') 
    likes = models.ManyToManyField(CustomUser, related_name='liked_tweets', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    parent_tweet = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='thread')
    is_thread = models.BooleanField(default=False)
    thread_position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Tweet by {self.user.username}"
    
    def is_retweet(self):
        return self.retweet is not None

    def retweet_count(self):
        return self.retweets.count()

    def get_replies(self):
        return self.replies.all()

    def is_retweeted_by(self, user):
        """Check if a user has retweeted this tweet."""
        return self.retweets.filter(user=user).exists()

    def remove_retweet(self, user):
        """Remove a retweet by the given user."""
        retweet = self.retweets.filter(user=user).first()
        if retweet:
            retweet.delete()
            return True
        return False
  
    def get_media(self):
        return self.media.all()  # Gets all associated media

    @property
    def is_thread_starter(self):
        return self.thread.exists() and not self.parent_tweet
      
    def get_full_thread(self):
        """Get complete thread including all parent and child tweets"""
        ancestors = self.get_ancestors()
        descendants = self.get_descendants()
        return list(ancestors) + [self] + list(descendants)
    
    def get_ancestors(self):
        """Get all parent tweets up to root"""
        ancestors = []
        current = self.parent_tweet
        while current:
            ancestors.append(current)
            current = current.parent_tweet
        return ancestors
    
    def get_descendants(self):
        """Get all child tweets"""
        return self.thread.all().order_by('thread_position')  

    def extract_hashtags(self):
        """Extract hashtags from tweet content."""
        hashtags = re.findall(r'#(\w+)', self.content)
        return set(hashtags)  # Remove duplicates

    def save(self, *args, **kwargs):
        # Automatically set is_thread flag when creating thread parent
        if self.parent_tweet is None and self.thread_position == 1:
            self.is_thread = True

        # Save the tweet first
        super().save(*args, **kwargs)

        # Extract and process hashtags
        for tag_name in self.extract_hashtags():
            hashtag, created = Hashtag.objects.get_or_create(name=tag_name.lower())
            hashtag.related_tweets.add(self)  # Link tweet to hashtag
            hashtag.update_trend_score()  # Update the trend score for the hashtag

class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    related_tweets = models.ManyToManyField(Tweet, blank=True)
    profile_image = models.ImageField(upload_to='hashtags/', null=True, blank=True)
    trend_score = models.IntegerField(default=0)  # Score to track popularity
    last_activity = models.DateTimeField(auto_now=True)  # Last time this hashtag was used

    def __str__(self):
        return self.name

    def update_trend_score(self):
        """Update the trend score based on recent activity."""
        recent_tweets = self.related_tweets.filter(created_at__gte=timezone.now() - timezone.timedelta(hours=24))
        self.trend_score = recent_tweets.count()
        self.save()

class Media(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='tweets/media/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_image(self):
        return self.media_type == 'image'

    @property
    def is_video(self):
        return self.media_type == 'video'