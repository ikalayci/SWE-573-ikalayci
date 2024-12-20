from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0047_comment_comment_type_comment_downvotes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='winner_comment',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='won_posts',
                to='posts.comment'
            ),
        ),
    ] 