# Generated by Django 3.2.13 on 2023-12-31 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0006_battingstatline_pitchingstatline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battingstatline',
            name='id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
    ]