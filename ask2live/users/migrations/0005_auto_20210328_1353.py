# Generated by Django 3.1.7 on 2021-03-28 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
