from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0029_team_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='RosterSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, blank=True, null=True)),
                ('date', models.DateField()),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statsdb.player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statsdb.team')),
            ],
            options={
                'unique_together': {('date', 'player')},
            },
        ),
    ]
