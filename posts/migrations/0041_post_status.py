# Generated by Django 4.2 on 2024-12-17 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0040_post_textures'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('unsolved', 'Unsolved'), ('solved', 'Solved')], default='unsolved', max_length=10),
        ),
    ]