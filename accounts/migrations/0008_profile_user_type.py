# Generated by Django 5.1.2 on 2024-12-18 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_deleteduser'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('member', 'Member')], default='member', max_length=10),
        ),
    ]
