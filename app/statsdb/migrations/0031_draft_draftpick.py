from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0030_rostersnapshot'),
    ]

    operations = [
        migrations.CreateModel(
            name='Draft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, blank=True, null=True)),
                ('year', models.IntegerField(unique=True)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('current_pick', models.IntegerField(default=1)),
                ('order', models.JSONField(default=list)),
                ('rounds', models.IntegerField(default=16)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DraftPick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, blank=True, null=True)),
                ('pick_number', models.IntegerField()),
                ('picked_at', models.DateTimeField(auto_now_add=True)),
                ('draft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picks', to='statsdb.draft')),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='statsdb.player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statsdb.team')),
            ],
            options={
                'ordering': ['pick_number'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='draftpick',
            unique_together={('draft', 'pick_number')},
        ),
    ]
