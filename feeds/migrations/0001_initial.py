# Generated by Django 3.2.5 on 2021-08-07 09:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Youtubechannel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_id', models.CharField(max_length=50)),
                ('title', models.TextField(blank=True)),
                ('creation_date', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('uploads', models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Youtubekeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Youtubeplaylist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('playlist_id', models.CharField(max_length=50, unique=True)),
                ('publish_date', models.DateTimeField(blank=True, null=True)),
                ('channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playlists', to='feeds.youtubechannel')),
            ],
        ),
        migrations.CreateModel(
            name='Youtubetag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Youtubevideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_id', models.CharField(max_length=50, unique=True)),
                ('thumbnail', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('title', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('playlist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='feeds.youtubeplaylist')),
                ('tags', models.ManyToManyField(blank=True, related_name='videos', to='feeds.Youtubetag')),
            ],
        ),
        migrations.AddField(
            model_name='youtubechannel',
            name='keywords',
            field=models.ManyToManyField(blank=True, related_name='channels', to='feeds.Youtubekeyword'),
        ),
    ]