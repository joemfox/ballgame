# Generated by Django 5.0 on 2024-03-04 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0007_rename_fan_h_seasonbattingstatline_fan_hits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seasonbattingstatline',
            name='cycle',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]