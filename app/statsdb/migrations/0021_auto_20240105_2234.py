# Generated by Django 3.2.13 on 2024-01-06 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0020_auto_20240105_2144'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='id',
        ),
        migrations.AlterField(
            model_name='player',
            name='fg_id',
            field=models.CharField(blank=True, default=1234567890, max_length=255, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
