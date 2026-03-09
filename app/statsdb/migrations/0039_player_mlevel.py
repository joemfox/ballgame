from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0038_alter_player_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='mlevel',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
