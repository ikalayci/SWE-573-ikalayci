# Generated by Django 4.2 on 2024-12-15 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0038_alter_post_materials'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='shapes',
            field=models.TextField(blank=True, null=True),
        ),
    ]