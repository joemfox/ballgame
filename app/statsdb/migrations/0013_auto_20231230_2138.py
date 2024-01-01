# Generated by Django 3.2.13 on 2023-12-31 02:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0012_auto_20231230_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='battingstatline',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pitchingstatline',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]