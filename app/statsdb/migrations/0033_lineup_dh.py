from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0032_fix_team_sequence'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineup',
            name='lineup_DH',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineup_DH', to='statsdb.player', to_field='fg_id'),
        ),
    ]
