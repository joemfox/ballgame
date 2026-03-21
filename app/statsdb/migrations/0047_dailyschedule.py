from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statsdb', '0046_update_scoring_values'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailySchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('roster_lock_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
