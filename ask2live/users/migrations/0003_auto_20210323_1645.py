# Generated by Django 3.1.7 on 2021-03-23 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210319_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='work_company',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='work_field',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
