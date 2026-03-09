from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0034_fix_pk_id_auto_created'),
    ]

    operations = [
        migrations.RemoveField(model_name='lineup', name='lineup_LF'),
        migrations.RemoveField(model_name='lineup', name='lineup_CF'),
        migrations.RemoveField(model_name='lineup', name='lineup_RF'),
        migrations.AddField(
            model_name='lineup',
            name='lineup_OF1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineup_OF1', to='statsdb.player', to_field='fg_id'),
        ),
        migrations.AddField(
            model_name='lineup',
            name='lineup_OF2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineup_OF2', to='statsdb.player', to_field='fg_id'),
        ),
        migrations.AddField(
            model_name='lineup',
            name='lineup_OF3',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineup_OF3', to='statsdb.player', to_field='fg_id'),
        ),
        migrations.AddField(
            model_name='lineup',
            name='lineup_OF4',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineup_OF4', to='statsdb.player', to_field='fg_id'),
        ),
        migrations.AddField(
            model_name='lineup',
            name='lineup_OF5',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineup_OF5', to='statsdb.player', to_field='fg_id'),
        ),
        migrations.AddField(
            model_name='lineup',
            name='lineup_UTIL',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineup_UTIL', to='statsdb.player', to_field='fg_id'),
        ),
    ]
