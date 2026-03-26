from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0048_battingstatline_inning'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='role',
            new_name='level',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='role_type',
            new_name='role',
        ),
    ]
