# Generated by Django 3.1.7 on 2021-03-17 08:32

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('holes', '0004_remove_livehole_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hole',
            name='status',
            field=models.CharField(choices=[('NOT_START', 'NOT_START'), ('DOING', 'DOING'), ('DONE', 'DONE')], default='NOT_START', max_length=12),
        ),
        migrations.AlterField(
            model_name='livehole',
            name='audience_list',
            field=django_mysql.models.ListTextField(models.IntegerField(), default='', size=30),
        ),
    ]