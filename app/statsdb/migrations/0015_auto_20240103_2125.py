# Generated by Django 3.2.13 on 2024-01-04 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0014_auto_20240103_1225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='team',
            new_name='team_assigned',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_2b',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_3b',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_ab',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_avg',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_bb',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_bb_9',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_bb_pct',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_er',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_era',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_g',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_gs',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_ha',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_hits',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_hits_9',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_hr',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_hr_9',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_hra',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_ip',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_iso',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_k',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_k_9',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_k_pct',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_obp',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_pbb',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_pk',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_plate_appearances',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_rbi',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_runs',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_sb',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_slg',
        ),
        migrations.RemoveField(
            model_name='team',
            name='ls_whip',
        ),
        migrations.AddField(
            model_name='team',
            name='lineup',
            field=models.ManyToManyField(to='statsdb.Player'),
        ),
    ]
