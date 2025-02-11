# Generated by Django 3.2.13 on 2022-08-04 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resource_tracker', '0009_auto_20220303_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcepoolattributedefinition',
            name='red_threshold_percent_consumed',
            field=models.IntegerField(blank=True, default=90, help_text='Threshold at which the color changes to red. Threshold is reverse when the red threshold is lower than the yellow threshold.', verbose_name='Red threshold percent consumed'),
        ),
        migrations.AddField(
            model_name='resourcepoolattributedefinition',
            name='yellow_threshold_percent_consumed',
            field=models.IntegerField(blank=True, default=80, help_text='Threshold at which the color changes to yellow. Threshold is reverse when the red threshold is lower than the yellow threshold.', verbose_name='Yellow threshold percent consumed'),
        ),
    ]
