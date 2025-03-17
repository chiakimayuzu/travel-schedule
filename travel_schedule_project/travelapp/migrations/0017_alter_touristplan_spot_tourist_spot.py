# Generated by Django 5.1.5 on 2025-03-17 09:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelapp', '0016_alter_userreview_user_touristplan_touristplan_spot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='touristplan_spot',
            name='tourist_spot',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tourist_plan_spots', to='travelapp.touristspot'),
        ),
    ]
