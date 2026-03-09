from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0040_update_fan_hits_and_outs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teampitchingstatline',
            name='bs',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='teampitchingstatline',
            name='quality_start',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='teampitchingstatline',
            name='perfect_game',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='teampitchingstatline',
            name='no_hitter',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='teampitchingstatline',
            name='relief_loss',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
