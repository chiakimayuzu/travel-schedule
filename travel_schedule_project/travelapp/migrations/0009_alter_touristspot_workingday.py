# Generated by Django 5.1.5 on 2025-03-10 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelapp', '0008_alter_touristspot_workingday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='touristspot',
            name='workingday',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
