# Generated by Django 3.2.5 on 2021-08-12 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0003_auto_20210812_1523'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='action',
        ),
        migrations.AddField(
            model_name='notification',
            name='actions',
            field=models.ManyToManyField(blank=True, related_name='_nodes_notification_actions_+', to='nodes.Action'),
        ),
    ]
