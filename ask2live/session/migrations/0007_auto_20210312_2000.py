# Generated by Django 3.1.7 on 2021-03-12 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0006_auto_20210312_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='host_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='live_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='question_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='rating',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='status',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='target_demand',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='wish_user_list',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]