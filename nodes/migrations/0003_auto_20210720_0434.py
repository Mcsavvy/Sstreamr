# Generated by Django 3.2.5 on 2021-07-20 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0002_auto_20210708_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='facebook',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='node',
            name='instagram',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='node',
            name='twitter',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]