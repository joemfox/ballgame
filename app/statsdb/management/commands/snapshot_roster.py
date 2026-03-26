import datetime
from django.core.management.base import BaseCommand
from statsdb import models

LINEUP_SLOTS = [
    'lineup_C', 'lineup_1B', 'lineup_2B', 'lineup_SS', 'lineup_3B',
    'lineup_OF1', 'lineup_OF2', 'lineup_OF3', 'lineup_OF4', 'lineup_OF5',
    'lineup_DH', 'lineup_UTIL',
    'lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5',
    'lineup_RP1', 'lineup_RP2', 'lineup_RP3',
]


class Command(BaseCommand):
    help = 'Snapshot current roster ownership and lineups for a given date (default: today). Run before daily game import.'

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

        lineup_count = 0
        for lineup in models.Lineup.objects.select_related('lineup_team').all():
            slot_data = {}
            for slot in LINEUP_SLOTS:
                player = getattr(lineup, slot)
                slot_data[slot] = player.fg_id if player else None
            models.LineupSnapshot.objects.update_or_create(
                date=snap_date,
                team=lineup.lineup_team,
                defaults=slot_data,
            )
            lineup_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Snapshotted {count} players and {lineup_count} lineups for {snap_date}'
        ))
