from django.conf import settings
from django.db import migrations

PV = settings.POINT_VALUES_HIT


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0039_player_mlevel'),
    ]

    operations = [
        migrations.RunSQL(
            f"""CREATE OR REPLACE FUNCTION fan_hits(numeric) RETURNS numeric IMMUTABLE AS $$
SELECT CASE
  WHEN $1 <= {PV['hits_bp_1']} THEN {PV['hits_max_1']} * $1
  WHEN $1 > {PV['hits_bp_1']} AND $1 <= {PV['hits_bp_2']}
    THEN ({PV['hits_bp_1']} * {PV['hits_max_1']}) + ($1 - {PV['hits_bp_1']}) * {PV['hits_max_2']}
  ELSE
    ({PV['hits_bp_1']} * {PV['hits_max_1']}) + ({PV['hits_bp_2']} - {PV['hits_bp_1']}) * {PV['hits_max_2']} + ($1 - {PV['hits_bp_2']}) * {PV['hits_min_2']}
END; $$ LANGUAGE SQL;""",
            "DROP FUNCTION IF EXISTS fan_hits(numeric);"
        ),
        migrations.RunSQL(
            f"""CREATE OR REPLACE FUNCTION fan_outs(numeric) RETURNS numeric IMMUTABLE AS $$
SELECT CASE
  WHEN $1 <= {PV['outs_bp_1']} THEN {PV['outs_max_1']} * $1
  WHEN $1 > {PV['outs_bp_1']} AND $1 <= {PV['outs_bp_2']}
    THEN ({PV['outs_bp_1']} * {PV['outs_max_1']}) + ($1 - {PV['outs_bp_1']}) * {PV['outs_max_2']}
  ELSE
    ({PV['outs_bp_1']} * {PV['outs_max_1']}) + ({PV['outs_bp_2']} - {PV['outs_bp_1']}) * {PV['outs_max_2']} + ($1 - {PV['outs_bp_2']}) * {PV['outs_min_2']}
END; $$ LANGUAGE SQL;""",
            "DROP FUNCTION IF EXISTS fan_outs(numeric);"
        ),
    ]
