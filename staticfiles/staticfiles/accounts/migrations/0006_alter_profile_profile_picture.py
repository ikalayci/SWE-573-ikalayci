# Generated by Django 4.2 on 2024-11-30 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='default-profile-picture.png', upload_to='profile_pictures/'),
        ),
    ]