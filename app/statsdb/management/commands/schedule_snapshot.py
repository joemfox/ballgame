import datetime
import pytz
import statsapi
from django.core.management.base import BaseCommand
from statsdb import models


class Command(BaseCommand):
    help = 'Find first game time for a date, store as roster lock time, and print ISO datetime for at-job scheduling.'

    def add_arguments(self, parser):
        parser.add_argument('date', nargs='?', default=None, type=str,
                            help='Date in YYYY-MM-DD format (default: today)')

    def handle(self, *args, **options):
        date_str = options.get('date')
        if date_str:
            target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = datetime.date.today()

        formatted = target_date.strftime('%m/%d/%Y')
        schedule = statsapi.schedule(start_date=formatted, end_date=formatted)

        if not schedule:
            self.stderr.write(f'No games found for {target_date}')
            return

        earliest = None
        for game in schedule:
            dt_str = game.get('game_datetime')
            if dt_str:
                dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                if earliest is None or dt < earliest:
                    earliest = dt

        if earliest is None:
            self.stderr.write(f'No game_datetime found for any game on {target_date}')
            return

        models.DailySchedule.objects.update_or_create(
            date=target_date,
            defaults={'roster_lock_time': earliest},
        )

        # Print ISO UTC string for the shell script to convert with `date -d`
        self.stdout.write(earliest.isoformat())
