import django.db.models.expressions
from django.db import migrations, models
from statsdb.settings import POINT_VALUES_HIT, POINT_VALUES_PITCH


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0045_add_transaction_model'),
    ]

    operations = [
        # Update fan_cycle SQL function: -40 -> -100
        migrations.RunSQL(
            f"CREATE OR REPLACE FUNCTION fan_cycle(boolean) RETURNS numeric IMMUTABLE AS $$ SELECT CASE WHEN $1 THEN {POINT_VALUES_HIT['cycle']} ELSE 0 END; $$ LANGUAGE SQL;",
            reverse_sql="CREATE OR REPLACE FUNCTION fan_cycle(boolean) RETURNS numeric IMMUTABLE AS $$ SELECT CASE WHEN $1 THEN -40 ELSE 0 END; $$ LANGUAGE SQL;",
        ),
        # Update FAN_doubles: -2 -> -1.5
        migrations.RemoveField(model_name='battingstatline', name='FAN_doubles'),
        migrations.AddField(
            model_name='battingstatline',
            name='FAN_doubles',
            field=models.GeneratedField(
                db_persist=True,
                expression=django.db.models.expressions.CombinedExpression(
                    models.F('doubles'), '*', models.Value(POINT_VALUES_HIT['doubles'])
                ),
                output_field=models.FloatField(),
            ),
        ),
        # Update FAN_triples: -3 -> -4.5
        migrations.RemoveField(model_name='battingstatline', name='FAN_triples'),
        migrations.AddField(
            model_name='battingstatline',
            name='FAN_triples',
            field=models.GeneratedField(
                db_persist=True,
                expression=django.db.models.expressions.CombinedExpression(
                    models.F('triples'), '*', models.Value(POINT_VALUES_HIT['triples'])
                ),
                output_field=models.FloatField(),
            ),
        ),
        # Update FAN_balks: 5 -> 10
        migrations.RemoveField(model_name='pitchingstatline', name='FAN_balks'),
        migrations.AddField(
            model_name='pitchingstatline',
            name='FAN_balks',
            field=models.GeneratedField(
                db_persist=True,
                expression=django.db.models.expressions.CombinedExpression(
                    models.F('balks'), '*', models.Value(POINT_VALUES_PITCH['balks'])
                ),
                output_field=models.FloatField(),
            ),
        ),
    ]
