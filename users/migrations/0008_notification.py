# Generated by Django 5.0 on 2025-02-13 20:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0008_transaction_hashed_detail_transaction_previous_hash'),
        ('users', '0007_remove_userprofile_exchange_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='transactions.transaction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
