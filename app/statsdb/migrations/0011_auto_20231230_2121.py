# Generated by Django 3.2.13 on 2023-12-31 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0010_auto_20231230_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battingstatline',
            name='ab',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='assblood',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='avg',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='batting_order',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='bb',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='cs',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='doubles',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='e',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='h',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='hr',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='k',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='lob',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='obp',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='r',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='rbi',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='sb',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='slg',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='battingstatline',
            name='triples',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='balks',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='bb',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='bf',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='er',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='h',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='hr',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='k',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pitchingstatline',
            name='r',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]