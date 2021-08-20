# Generated by Django 3.2.5 on 2021-08-16 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0005_auto_20210813_1743'),
        ('feeds', '0004_auto_20210816_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagrampost',
            name='viewers',
            field=models.ManyToManyField(blank=True, related_name='viewed_instagram_posts', to='nodes.Node'),
        ),
        migrations.AlterField(
            model_name='youtubevideo',
            name='viewers',
            field=models.ManyToManyField(blank=True, related_name='viewed_youtube_videos', to='nodes.Node'),
        ),
    ]