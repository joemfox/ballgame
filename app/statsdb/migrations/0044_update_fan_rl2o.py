import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0043_alter_battingstatline_fan_bb_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='battingstatline',
            name='FAN_rl2o',
        ),
        migrations.AddField(
            model_name='battingstatline',
            name='FAN_rl2o',
            field=models.GeneratedField(
                db_persist=True,
                expression=django.db.models.expressions.CombinedExpression(
                    models.F('rl2o'), '*', models.Value(1)
                ),
                output_field=models.FloatField(),
            ),
        ),
    ]
