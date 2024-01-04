# Generated by Django 3.2.13 on 2024-01-04 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0016_auto_20240103_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='lineup',
            field=models.ManyToManyField(through='statsdb.Membership', to='statsdb.Player'),
        ),
    ]
