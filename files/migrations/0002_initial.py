# Generated by Django 4.2.2 on 2024-03-19 20:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='videoview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='videoview',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='files.video'),
        ),
        migrations.AddField(
            model_name='video',
            name='category',
            field=models.ManyToManyField(blank=True, related_name='videos', to='files.category'),
        ),
        migrations.AddField(
            model_name='video',
            name='channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='files.channel'),
        ),
        migrations.AddField(
            model_name='video',
            name='ignore_users',
            field=models.ManyToManyField(blank=True, related_name='ignored_videos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='video',
            name='playlist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='files.playlist'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playlists', to='files.channel'),
        ),
        migrations.AddField(
            model_name='like',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_videos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='like',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='files.video'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='files.video'),
        ),
        migrations.AddField(
            model_name='channeltodownload',
            name='categories',
            field=models.ManyToManyField(to='files.category'),
        ),
        migrations.AddField(
            model_name='channel',
            name='categories',
            field=models.ManyToManyField(related_name='channels', to='files.category'),
        ),
        migrations.AddField(
            model_name='channel',
            name='subscribers',
            field=models.ManyToManyField(blank=True, related_name='subscriptions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='adcontact',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='files.ad'),
        ),
        migrations.AddIndex(
            model_name='videoview',
            index=models.Index(models.F('viewed_at'), name='viewed_at_idx'),
        ),
    ]
