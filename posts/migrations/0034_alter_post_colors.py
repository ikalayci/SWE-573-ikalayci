# Generated by Django 4.2 on 2024-12-14 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0033_alter_tag_wikidata_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='colors',
            field=models.JSONField(blank=True, null=True),
        ),
    ]