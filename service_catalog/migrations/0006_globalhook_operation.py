# Generated by Django 3.2.12 on 2022-03-24 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0005_auto_20220302_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalhook',
            name='operation',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='service_catalog.operation'),
        ),
    ]