import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0042_add_sombrero'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='battingstatline',
            name='FAN_bb',
        ),
        migrations.AddField(
            model_name='battingstatline',
            name='FAN_bb',
            field=models.GeneratedField(db_persist=True, expression=django.db.models.expressions.CombinedExpression(models.F('bb'), '*', models.Value(-0.75)), output_field=models.FloatField()),
        ),
        migrations.RemoveField(
            model_name='battingstatline',
            name='FAN_cs',
        ),
        migrations.AddField(
            model_name='battingstatline',
            name='FAN_cs',
            field=models.GeneratedField(db_persist=True, expression=django.db.models.expressions.CombinedExpression(models.F('cs'), '*', models.Value(5)), output_field=models.FloatField()),
        ),
    ]
