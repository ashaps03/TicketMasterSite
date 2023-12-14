# Generated by Django 4.2.7 on 2023-12-14 06:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TM', '0005_remove_likedevent_event_likedevent_event_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('artist_id', models.CharField(max_length=255)),
                ('genre', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('image', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='SimilarArtist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', models.URLField()),
                ('url', models.URLField()),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TM.artist')),
            ],
        ),
        migrations.CreateModel(
            name='TopTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('album', models.CharField(max_length=255)),
                ('image', models.URLField()),
                ('url', models.URLField()),
                ('preview', models.URLField()),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TM.artist')),
            ],
        ),
        migrations.DeleteModel(
            name='FormCollection',
        ),
    ]
