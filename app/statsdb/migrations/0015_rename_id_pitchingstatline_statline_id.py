# Generated by Django 5.0 on 2024-03-09 21:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0014_pitchingstatline_bs'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pitchingstatline',
            old_name='id',
            new_name='statline_id',
        ),
    ]