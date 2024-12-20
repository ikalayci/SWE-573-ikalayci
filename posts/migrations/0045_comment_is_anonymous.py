from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0044_comment_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_anonymous',
            field=models.BooleanField(default=False),
        ),
    ]