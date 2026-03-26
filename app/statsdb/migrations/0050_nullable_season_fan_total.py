from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0049_rename_role_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seasonbattingstatline',
            name='FAN_total',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='seasonpitchingstatline',
            name='FAN_total',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True),
        ),
        migrations.RunSQL(
            "UPDATE statsdb_seasonbattingstatline SET \"FAN_total\" = NULL WHERE \"FAN_total\" = 0",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "UPDATE statsdb_seasonpitchingstatline SET \"FAN_total\" = NULL WHERE \"FAN_total\" = 0",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
