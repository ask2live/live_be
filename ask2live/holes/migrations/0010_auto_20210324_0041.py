# Generated by Django 3.1.7 on 2021-03-23 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('holes', '0009_participants_leaved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livehole',
            name='id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
