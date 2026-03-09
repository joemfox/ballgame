from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0036_update_fan_k_breakpoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='battingstatline',
            name='game_type',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='pitchingstatline',
            name='game_type',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
