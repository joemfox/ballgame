from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('statsdb', '0033_lineup_dh'),
    ]
    operations = [
        migrations.AlterField(
            model_name='battingstatline',
            name='pk_id',
            field=models.BigAutoField(verbose_name='ID', null=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='pk_id',
            field=models.BigAutoField(verbose_name='ID', null=False, primary_key=True, serialize=False),
        ),
    ]
