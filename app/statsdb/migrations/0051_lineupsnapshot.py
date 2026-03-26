from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0050_nullable_season_fan_total'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineupSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statsdb.team')),
                ('lineup_C', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_1B', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_2B', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_SS', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_3B', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_OF1', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_OF2', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_OF3', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_OF4', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_OF5', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_DH', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_UTIL', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_SP1', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_SP2', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_SP3', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_SP4', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_SP5', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_RP1', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_RP2', models.CharField(blank=True, max_length=50, null=True)),
                ('lineup_RP3', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'unique_together': {('date', 'team')},
            },
        ),
    ]
