# Generated by Django 5.0 on 2024-03-08 21:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0009_rename_fan_hits_battingstatline_fan_h_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamBattingStatLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('date', models.DateField()),
                ('games', models.IntegerField(blank=True, null=True)),
                ('ab', models.IntegerField(blank=True, null=True)),
                ('r', models.IntegerField(blank=True, null=True)),
                ('h', models.IntegerField(blank=True, null=True)),
                ('outs', models.IntegerField(blank=True, null=True)),
                ('doubles', models.IntegerField(blank=True, null=True)),
                ('triples', models.IntegerField(blank=True, null=True)),
                ('hr', models.IntegerField(blank=True, null=True)),
                ('rbi', models.IntegerField(blank=True, null=True)),
                ('bb', models.IntegerField(blank=True, null=True)),
                ('k', models.IntegerField(blank=True, null=True)),
                ('lob', models.IntegerField(blank=True, null=True)),
                ('sb', models.IntegerField(blank=True, null=True)),
                ('cs', models.IntegerField(blank=True, null=True)),
                ('e', models.IntegerField(blank=True, null=True)),
                ('k_looking', models.IntegerField(blank=True, null=True)),
                ('rl2o', models.IntegerField(blank=True, null=True)),
                ('cycle', models.IntegerField(blank=True, null=True)),
                ('gidp', models.IntegerField(blank=True, null=True)),
                ('po', models.IntegerField(blank=True, null=True)),
                ('outfield_assists', models.IntegerField(blank=True, null=True)),
                ('FAN_ab', models.FloatField(blank=True, null=True)),
                ('FAN_r', models.FloatField(blank=True, null=True)),
                ('FAN_h', models.FloatField(blank=True, null=True)),
                ('FAN_outs', models.FloatField(blank=True, null=True)),
                ('FAN_doubles', models.FloatField(blank=True, null=True)),
                ('FAN_triples', models.FloatField(blank=True, null=True)),
                ('FAN_hr', models.FloatField(blank=True, null=True)),
                ('FAN_rbi', models.FloatField(blank=True, null=True)),
                ('FAN_bb', models.FloatField(blank=True, null=True)),
                ('FAN_k', models.FloatField(blank=True, null=True)),
                ('FAN_lob', models.FloatField(blank=True, null=True)),
                ('FAN_sb', models.FloatField(blank=True, null=True)),
                ('FAN_cs', models.FloatField(blank=True, null=True)),
                ('FAN_e', models.FloatField(blank=True, null=True)),
                ('FAN_k_looking', models.FloatField(blank=True, null=True)),
                ('FAN_rl2o', models.FloatField(blank=True, null=True)),
                ('FAN_cycle', models.FloatField(blank=True, null=True)),
                ('FAN_gidp', models.FloatField(blank=True, null=True)),
                ('FAN_po', models.FloatField(blank=True, null=True)),
                ('FAN_outfield_assists', models.FloatField(blank=True, null=True)),
                ('FAN_total', models.FloatField(default=0.0)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statsdb.team')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
