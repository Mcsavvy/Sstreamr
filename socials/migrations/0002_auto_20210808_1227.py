# Generated by Django 3.2.5 on 2021-08-08 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0002_remove_node_instagram'),
        ('socials', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instagramprofile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('username', models.CharField(max_length=50)),
                ('bio', models.TextField(blank=True)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='profiles/instagram')),
                ('external_url', models.URLField(blank=True, null=True)),
                ('verified', models.BooleanField()),
                ('private', models.BooleanField()),
                ('is_authenticated', models.BooleanField(default=False)),
                ('node', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='instagram', to='nodes.node')),
            ],
        ),
        migrations.DeleteModel(
            name='Instagram',
        ),
    ]