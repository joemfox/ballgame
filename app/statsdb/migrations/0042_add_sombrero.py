from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0041_teampitchingstatline_bool_to_int'),
    ]

    operations = [
        migrations.AddField(
            model_name='battingstatline',
            name='sombrero',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='seasonbattingstatline',
            name='sombrero',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teambattingstatline',
            name='sombrero',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
