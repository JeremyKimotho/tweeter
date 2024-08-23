# Generated by Django 5.0.6 on 2024-08-23 03:00

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('posts', '0004_post_bookmarks_remove_post_comments_and_more'),
        ('user_profile', '0003_remove_userprofile_comments_remove_userprofile_likes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostTraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(default=1)),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='posts.post')),
                ('poster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
            ],
        ),
    ]
