# Generated by Django 5.0 on 2025-03-03 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0009_tweet_is_thread_tweet_parent_tweet_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='hashtags/')),
                ('trend_score', models.IntegerField(default=0)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('related_tweets', models.ManyToManyField(blank=True, to='community.tweet')),
            ],
        ),
    ]
