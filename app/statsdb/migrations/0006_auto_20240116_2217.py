# Generated by Django 5.0 on 2024-01-17 03:00
from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0005_remove_battingstatline_fan_bb_and_more'),
    ]

    operations = [
        migrations.RunSQL(f"CREATE OR REPLACE FUNCTION fan_outs(numeric) RETURNS numeric IMMUTABLE AS $$ SELECT CASE WHEN $1 <= {settings.POINT_VALUES_HIT['outs_bp_1']} THEN {settings.POINT_VALUES_HIT['outs_max_1']} * $1 ELSE {settings.POINT_VALUES_HIT['outs_min_1']} * {settings.POINT_VALUES_HIT['outs_bp_1']} + $1 - {settings.POINT_VALUES_HIT['outs_bp_1']} END; $$ LANGUAGE SQL;",('DROP FUNCTION IF EXISTS fan_outs();')),
        migrations.RunSQL(f"CREATE OR REPLACE FUNCTION fan_hits(numeric) RETURNS numeric IMMUTABLE AS $$ SELECT CASE WHEN $1 <= {settings.POINT_VALUES_HIT['hits_bp_1']} THEN {settings.POINT_VALUES_HIT['hits_max_1']} * $1 WHEN $1 > {settings.POINT_VALUES_HIT['hits_bp_1']} and $1 <= {settings.POINT_VALUES_HIT['hits_bp_2']} THEN ({settings.POINT_VALUES_HIT['hits_bp_1']} * {settings.POINT_VALUES_HIT['hits_max_1']}) + ($1 - {settings.POINT_VALUES_HIT['hits_bp_1']}) * {settings.POINT_VALUES_HIT['hits_max_2']} ELSE ({settings.POINT_VALUES_HIT['hits_bp_1']} * {settings.POINT_VALUES_HIT['hits_max_1']}) + ({settings.POINT_VALUES_HIT['hits_bp_2']} - {settings.POINT_VALUES_HIT['hits_bp_1']}) * {settings.POINT_VALUES_HIT['hits_max_2']} + ($1 - {settings.POINT_VALUES_HIT['hits_bp_2']}) * {settings.POINT_VALUES_HIT['hits_min_2']} END; $$ LANGUAGE SQL;",('DROP FUNCTION IF EXISTS fan_hits();'))
    ]