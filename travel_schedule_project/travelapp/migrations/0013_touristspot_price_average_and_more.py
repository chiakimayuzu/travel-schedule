# Generated by Django 5.1.5 on 2025-03-11 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelapp', '0012_alter_touristspot_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='touristspot',
            name='price_average',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='touristspot',
            name='review_score_average',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='touristspot',
            name='staytime_average',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
