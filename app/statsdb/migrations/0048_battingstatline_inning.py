from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0047_dailyschedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='battingstatline',
            name='inning',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='battingstatline',
            name='inning_half',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='battingstatline',
            name='game_complete',
            field=models.BooleanField(null=True),
        ),
    ]
