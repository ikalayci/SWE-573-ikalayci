# Generated by Django 4.2 on 2024-12-20 15:30:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0049_comment_answer_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='hint_link',
            field=models.URLField(blank=True, help_text='Optional for hints. Must be a valid URL', null=True),
        ),
    ] 