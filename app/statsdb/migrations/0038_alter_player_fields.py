import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0037_statline_game_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='position',
            field=models.CharField(choices=[('P', 'Pitcher'), ('IF', 'Infield'), ('OF', 'Outfield'), ('C', 'Catcher'), ('DH', 'DH'), ('IF-OF', 'IF-OF'), ('OF-P', 'OF-P'), ('IF-P', 'IF-P')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='positions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('SP', 'Starter'), ('RP', 'Reliever'), ('C', 'Catcher'), ('1B', 'First base'), ('2B', 'Second base'), ('SS', 'Shortstop'), ('3B', 'Third base'), ('LF', 'Left field'), ('CF', 'Center field'), ('RF', 'Right field'), ('DH', 'Designated hitter')], max_length=2, null=True), size=None),
        ),
    ]
