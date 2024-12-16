# Generated by Django 4.2 on 2024-12-14 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0034_alter_post_colors'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='era',
            field=models.CharField(blank=True, choices=[('AC', 'AC'), ('BC', 'BC')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='colors',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='time_period',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
