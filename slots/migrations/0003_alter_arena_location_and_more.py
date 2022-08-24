# Generated by Django 4.1 on 2022-08-24 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0002_sport_cover_picture_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arena',
            name='location',
            field=models.URLField(blank=True, help_text='Google maps link for the location (Optional)', null=True),
        ),
        migrations.AlterField(
            model_name='slot',
            name='current_player_capacity',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Default is the max player capacity of the arena'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='current_spectator_capacity',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Default is the max spectator capacity of the arena', null=True),
        ),
        migrations.AlterField(
            model_name='sport',
            name='cover_picture',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
