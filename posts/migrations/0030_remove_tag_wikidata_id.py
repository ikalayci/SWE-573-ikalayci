# Generated by Django 4.2 on 2024-12-13 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0029_alter_tag_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='wikidata_id',
        ),
    ]
