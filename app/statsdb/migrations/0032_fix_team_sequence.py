from django.db import migrations


class Migration(migrations.Migration):
    """
    Reset the PostgreSQL sequence for statsdb_team.id to be greater than
    the current maximum id. This fixes "duplicate key" errors when creating
    new teams if the sequence drifted out of sync with the table data.
    """

    dependencies = [
        ('statsdb', '0031_draft_draftpick'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('statsdb_team', 'id'),
                    COALESCE((SELECT MAX(id) FROM statsdb_team), 0) + 1,
                    false
                );
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
