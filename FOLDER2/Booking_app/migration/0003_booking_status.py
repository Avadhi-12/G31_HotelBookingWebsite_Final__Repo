# Generated by Django 5.2 on 2025-04-12 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_app', '0002_booking_cancellation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(default='Confirmed', max_length=20),
        ),
    ]
