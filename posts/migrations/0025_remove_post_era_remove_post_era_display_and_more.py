# Generated by Django 4.2 on 2024-12-12 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0024_post_era'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='era',
        ),
        migrations.RemoveField(
            model_name='post',
            name='era_display',
        ),
        migrations.RemoveField(
            model_name='post',
            name='era_hidden',
        ),
        migrations.RemoveField(
            model_name='post',
            name='time_period_backend',
        ),
        migrations.RemoveField(
            model_name='post',
            name='time_period_display',
        ),
        migrations.AddField(
            model_name='post',
            name='time_period',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]