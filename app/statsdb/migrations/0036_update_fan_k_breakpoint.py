from django.conf import settings
from django.db import migrations

PV = settings.POINT_VALUES_HIT


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0035_lineup_of_util'),
    ]

    operations = [
        migrations.RunSQL(
            f"""CREATE OR REPLACE FUNCTION fan_k(numeric) RETURNS numeric IMMUTABLE AS $$
SELECT CASE
  WHEN $1 <= {PV['k_bp_1']} THEN {PV['k_max_1']} * $1
  WHEN $1 > {PV['k_bp_1']} AND $1 <= {PV['k_bp_2']}
    THEN ({PV['k_bp_1']} * {PV['k_max_1']}) + ($1 - {PV['k_bp_1']}) * {PV['k_max_2']}
  WHEN $1 > {PV['k_bp_2']} AND $1 <= {PV['k_bp_3']}
    THEN ({PV['k_bp_1']} * {PV['k_max_1']}) + ({PV['k_bp_2']} - {PV['k_bp_1']}) * {PV['k_max_2']} + ($1 - {PV['k_bp_2']}) * {PV['k_max_3']}
  ELSE
    ({PV['k_bp_1']} * {PV['k_max_1']}) + ({PV['k_bp_2']} - {PV['k_bp_1']}) * {PV['k_max_2']} + ({PV['k_bp_3']} - {PV['k_bp_2']}) * {PV['k_max_3']} + ($1 - {PV['k_bp_3']}) * {PV['k_min_3']}
END; $$ LANGUAGE SQL;""",
            "DROP FUNCTION IF EXISTS fan_k(numeric);"
        ),
    ]
