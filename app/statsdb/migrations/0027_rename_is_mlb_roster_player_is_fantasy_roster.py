from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0026_alter_pitchingstatline_fan_total_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='is_mlb_roster',
            new_name='is_fantasy_roster',
        ),
    ]
