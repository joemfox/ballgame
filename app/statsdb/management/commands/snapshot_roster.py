import datetime
from django.core.management.base import BaseCommand
from statsdb import models


class Command(BaseCommand):
    help = 'Snapshot current roster ownership for a given date (default: today). Run before daily game import.'

    def add_arguments(self, parser):
        parser.add_argument('date', nargs='?', default=None, type=str,
                            help='Date in YYYY-MM-DD format (default: today)')

    def handle(self, *args, **options):
        date_str = options.get('date')
        if date_str:
            snap_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            snap_date = datetime.date.today()

        players = models.Player.objects.filter(
            team_assigned__isnull=False
        ).select_related('team_assigned')

        count = 0
        for player in players:
            models.RosterSnapshot.objects.update_or_create(
                date=snap_date,
                player=player,
                defaults={'team': player.team_assigned},
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Snapshotted {count} players for {snap_date}'
        ))
