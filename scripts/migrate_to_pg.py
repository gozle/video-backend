import os
import sys
import django
from django.db import connection, InterfaceError

# Load Django settings
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'tmtubBackend.settings'
django.setup()

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from files.models import Channel, Ad, Category, Icon, Playlist, Video, VideoView, Like
from users.models import User, TariffPlan, TariffSubscription, Client


def migrate_category(category):
    if Category.objects.using('pg').filter(name=category.name).count():
        return
    new_category = Category(
        name=category.name,
        icon=category.icon,
        turkmen=category.turkmen,
        english=category.english,
        russian=category.russian,
    )
    new_category.save(using='pg')


def migrate_categories():
    objs = Category.objects.all()
    django.db.connections.close_all()
    with ProcessPoolExecutor() as executor:
        for out in executor.map(migrate_category, objs):
            if out:
                print(out)


def migrate_user(user):
    if User.objects.using('pg').filter(user_id=user.user_id).count():
        return
    new_user = User(
        username=user.username,
        user_id=user.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
        avatar=user.avatar,
        access_token=user.access_token,
        refresh_token=user.refresh_token,
        source=user.source
    )
    new_user.save(using='pg')


def migrate_users():
    objs = [user for user in User.objects.all()]
    django.db.connections.close_all()
    with ProcessPoolExecutor() as executor:
        for out in executor.map(migrate_user, objs):
            if out:
                print(out)


def migrate_channel(channel):
    if not channel.channel_id:
        print('skipping c1', channel.name)
        return
    if Channel.objects.using('pg').filter(channel_id=channel.channel_id).exists():
        print('skipping c2', channel.name)
        return
    else:
        new_channel = Channel(
            channel_id=channel.channel_id,
            name=channel.name,
            description=channel.description,
            keywords=channel.keywords,
            avatar=channel.avatar,
            banner=channel.banner,
            all_video=channel.all_video,
            view=channel.view,
            server=channel.server,
            last_checked=channel.last_checked,
            premium=channel.premium,
            geo_protected=channel.geo_protected
        )
        new_channel.save(using='pg')

    new_channel = Channel.objects.using('pg').get(channel_id=channel.channel_id)

    sub_user_ids = []
    for user in channel.subscribers.all():
        try:
            sub_user_ids.append(user.user_id)
        except InterfaceError:
            django.db.connections.close_all()
            sub_user_ids.append(user.user_id)
    users = User.objects.using('pg').filter(user_id__in=sub_user_ids)
    if users:
        for i in users:
            try:
                new_channel.subscribers.add(i)
            except InterfaceError:
                django.db.connections.close_all()
                new_channel.subscribers.add(i)

    category_names = [cat.name for cat in channel.categories.all()]
    categories = Category.objects.using('pg').filter(name__in=category_names)
    if categories:
        for i in categories:
            new_channel.categories.add(i)


def migrate_channels():
    objs = [channel for channel in Channel.objects.all()]
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_channel, objs):
            if out:
                print(out)


def migrate_ad(ad):
    if Ad.objects.using('pg').filter(link=ad.link).count():
        return
    new_ad = Ad(
        title_tm=ad.title_tm,
        title_en=ad.title_en,
        title_ru=ad.title_ru,
        description_en=ad.description_en,
        description_tm=ad.description_tm,
        description_ru=ad.description_ru,
        duration=ad.duration,
        thumbnail_en=ad.thumbnail_en,
        thumbnail_tm=ad.thumbnail_tm,
        thumbnail_ru=ad.thumbnail_ru,
        link=ad.link,
        m3u8_en=ad.m3u8_en,
        m3u8_ru=ad.m3u8_ru,
        m3u8_tm=ad.m3u8_tm,
        view=ad.view,
        click=ad.click,
        video_en=ad.video_en,
        video_tm=ad.video_tm,
        video_ru=ad.video_ru,
        category=ad.category,
        is_active=ad.is_active
    )
    new_ad.save(using='pg')


def migrate_ads():
    objs = Ad.objects.all()
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_ad, objs):
            if out:
                print(out)


def migrate_icon(icon):
    if Icon.objects.using('pg').filter(slug=icon.slug).exists():
        return
    new_icon = Icon(
        slug=icon.slug,
        icon=icon.icon,
        turkmen=icon.turkmen,
        english=icon.english,
        russian=icon.russian
    )
    new_icon.save(using='pg')


def migrate_icons():
    objs = Icon.objects.all()
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_icon, objs):
            if out:
                print(out)


def migrate_playlist(playlist):
    if Playlist.objects.using('pg').filter(playlist_id=playlist.playlist_id).count():
        return
    if Channel.objects.using('pg').filter(channel_id=playlist.channel.channel_id).count() < 1:
        return
    channel = Channel.objects.using('pg').get(channel_id=playlist.channel.channel_id)
    new_playlist = Playlist(
        playlist_id=playlist.playlist_id,
        title=playlist.title,
        thumbnail=playlist.thumbnail,
        view=playlist.view,
        server=playlist.server,
        channel=channel
    )
    new_playlist.save(using='pg')


def migrate_playlists():
    objs = [playlist for playlist in Playlist.objects.all()]
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_playlist, objs):
            if out:
                print(out)


def migrate_video(video):
    if not video.video_id:
        return
    if Video.objects.using('pg').filter(video_id=video.video_id).exists():
        return
    if Channel.objects.using('pg').filter(channel_id=video.channel.channel_id).count() < 1:
        return
    channel = Channel.objects.using('pg').get(channel_id=video.channel.channel_id)
    if video.playlist:
        if Playlist.objects.using('pg').filter(playlist_id=video.playlist.playlist_id).count() < 1:
            return
        playlist = Playlist.objects.using('pg').get(playlist_id=video.playlist.playlist_id)
    else:
        playlist = None
    new_video = Video(
        video_id=video.video_id,
        title=video.title,
        description=video.description,
        m3u8=video.m3u8,
        thumbnail=video.thumbnail,
        subtitle=video.subtitle,
        view=video.view,
        video=video.video,
        type=video.type,
        date=video.date,
        published_at=video.published_at,
        duration=video.duration,
        expansion=video.expansion,
        expansion_m=video.expansion_m,
        channel=channel,
        playlist=playlist,
        premium=video.premium,
        is_processing=video.is_processing,
        server=video.server,
        important=video.important,
    )
    new_video.save(using='pg')
    user_ids = [user.user_id for user in video.ignore_users.all()]

    new_video = Video.objects.using('pg').get(video_id=video.video_id)

    users = User.objects.using('pg').filter(user_id__in=user_ids)
    if users:
        for i in users:
            new_video.ignore_users.add(i)

    category_names = [cat.name for cat in video.category.all()]
    categories = Category.objects.using('pg').filter(name__in=category_names)
    if categories:
        for i in categories:
            new_video.category.add(i)


def migrate_videos():
    objs = [video for video in Video.objects.all()]
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_video, objs):
            if out:
                print(out)


def migrate_video_view(video_view):
    if Video.objects.using('pg').filter(video_id=video_view.video.video_id).count() < 1:
        return
    if User.objects.using('pg').filter(user_id=video_view.user.user_id).count() < 1:
        return
    video = Video.objects.using('pg').get(video_id=video_view.video.video_id)
    user = User.objects.using('pg').get(user_id=video_view.user.user_id)
    new_video_view = VideoView(
        viewed_at=video_view.viewed_at,
        video=video,
        user=user
    )
    new_video_view.save(using='pg')


def migrate_video_views():
    objs = VideoView.objects.all()
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_video_view, objs):
            if out:
                print(out)


def migrate_like(like):
    if Video.objects.using('pg').filter(video_id=like.video.video_id).count() < 1:
        return
    if User.objects.using('pg').filter(user_id=like.user.user_id).count() < 1:
        return
    video = Video.objects.using('pg').get(video_id=like.video.video_id)
    user = User.objects.using('pg').get(user_id=like.user.user_id)
    new_like = Like(
        video=video,
        user=user
    )
    new_like.save(using='pg')


def migrate_likes():
    objs = Like.objects.all()
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_like, objs):
            if out:
                print(out)


def migrate_tariff_plan(tariff_plan):
    new_tariff_plan = TariffPlan(
        name=tariff_plan.name,
        description=tariff_plan.description,
        price=tariff_plan.price,
        active=tariff_plan.active,
        can_download=tariff_plan.can_download,
        less_ad=tariff_plan.less_ad,
        live_videos=tariff_plan.live_videos,
        premium_channels=tariff_plan.premium_channels
    )
    new_tariff_plan.save(using='pg')


def migrate_tariff_plans():
    objs = TariffPlan.objects.all()
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_tariff_plan, objs):
            if out:
                print(out)


def migrate_tariff_sub(tariff_sub):
    plan = TariffPlan.objects.using('pg').get(name=tariff_sub.plan.name)
    if User.objects.using('pg').filter(user_id=tariff_sub.user.user_id).count() < 1:
        return
    user = User.objects.using('pg').get(user_id=tariff_sub.user.user_id)
    new_tariff_sub = TariffSubscription(
        id=tariff_sub.id,
        plan=plan,
        user=user,
        expires_at=tariff_sub.expires_at,
        active=tariff_sub.active
    )
    new_tariff_sub.save(using='pg')


def migrate_tariff_subs():
    objs = TariffSubscription.objects.all()
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_tariff_sub, objs):
            if out:
                print(out)


def migrate_client(client):
    new_client = Client(
        client_id=client.client_id,
        client_secret=client.client_secret,
        callback_uri=client.callback_uri,
        login_uri=client.login_uri,
        token_uri=client.token_uri,
        resource_uri=client.resource_uri
    )
    new_client.save(using='pg')


def migrate_clients():
    objs = Client.objects.all()
    django.db.connections.close_all()
    with ThreadPoolExecutor() as executor:
        for out in executor.map(migrate_client, objs):
            if out:
                print(out)


print('Ads migrating...')
migrate_ads()
print('Ads migrated!')
print('Migrating icons')
migrate_icons()
print('Icons migrated!')
print('Users migrating')
migrate_users()
print('Users migrated!')
print('Categories migrating')
migrate_categories()
print('Categories migrated!')
print('Channels migrating')
migrate_channels()
print('Channels migrated!')
print('Playlists migrationg!')
migrate_playlists()
print('Playlists migrated!')
print('Videos migrating!')
migrate_videos()
print('Videos migrated!')
# print('Migrating video views...')
# migrate_video_views()
# print('Video Views migrated!')
print('Videos Like migrating')
migrate_likes()
print('Like migrated!')
print('Tariff plans migrating')
migrate_tariff_plans()
print('Tariff plans migrated!')
print('Tariff subs migrating')
migrate_tariff_subs()
print('Tariff subs migrated!')
print('clients migrating')
migrate_clients()
print('clients migrated!')
