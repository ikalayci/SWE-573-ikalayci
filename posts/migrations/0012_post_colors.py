# Generated by Django 4.2 on 2024-12-08 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_remove_post_colors_post_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='colors',
            field=models.TextField(blank=True, null=True),
        ),
    ]
