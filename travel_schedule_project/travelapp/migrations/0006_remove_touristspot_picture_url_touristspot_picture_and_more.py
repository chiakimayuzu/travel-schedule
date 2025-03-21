# Generated by Django 5.1.5 on 2025-03-10 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelapp', '0005_keyword_rename_tourist_spot_touristspot_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='touristspot',
            name='picture_url',
        ),
        migrations.AddField(
            model_name='touristspot',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='tourist_spot_images/'),
        ),
        migrations.AlterField(
            model_name='touristspot',
            name='workingday',
            field=models.IntegerField(blank=True, choices=[(1, '月曜'), (2, '火曜'), (3, '水曜'), (4, '木曜'), (5, '金曜'), (6, '土曜'), (7, '日曜'), (8, '年中無休'), (9, '不定休')], null=True),
        ),
    ]
