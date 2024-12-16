# Generated by Django 4.2 on 2024-12-12 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_post_era_hidden_post_time_period_backend_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='era_display',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='time_period_display',
            field=models.TextField(blank=True, null=True),
        ),
    ]
