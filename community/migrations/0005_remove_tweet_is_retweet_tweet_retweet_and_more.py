# Generated by Django 5.0 on 2025-02-19 19:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0004_tweet_is_retweet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tweet',
            name='is_retweet',
        ),
        migrations.AddField(
            model_name='tweet',
            name='retweet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='retweets', to='community.tweet'),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='content',
            field=models.TextField(blank=True, max_length=280),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='community.tweet'),
        ),
    ]
