# Generated by Django 3.1.7 on 2021-03-25 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hole_reservations', '0003_auto_20210325_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='target_demand',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
