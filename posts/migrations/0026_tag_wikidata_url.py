# Generated by Django 4.2 on 2024-12-13 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0025_remove_post_era_remove_post_era_display_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='wikidata_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
