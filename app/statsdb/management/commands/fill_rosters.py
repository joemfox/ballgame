"""
Randomly distribute unowned MLB players across all teams.

Usage:
    python manage.py fill_rosters                 # 15 players per team
    python manage.py fill_rosters --per-team 20   # 20 players per team
    python manage.py fill_rosters --clear         # clear rosters first, then fill
"""
import random
from django.core.management.base import BaseCommand
from statsdb.models import Player, Team, Lineup


class Command(BaseCommand):
    help = 'Randomly distribute unowned MLB players across all teams'

    def add_arguments(self, parser):
        parser.add_argument('--per-team', type=int, default=15,
                            help='Number of players per team (default: 15)')
        parser.add_argument('--clear', action='store_true',
                            help='Clear all existing roster assignments first')
        parser.add_argument('--mlb-only', action='store_true',
                            help='Only assign players with is_mlb=True (requires update_status_from_fg_rosters to have been run)')

    def handle(self, *args, **options):
        per_team = options['per_team']

        if options['clear']:
            # Clear all roster assignments and lineup slots
            Player.objects.update(team_assigned=None, is_owned=False)
            Lineup.objects.update(
                lineup_C=None, lineup_1B=None, lineup_2B=None,
                lineup_SS=None, lineup_3B=None, lineup_LF=None,
                lineup_CF=None, lineup_RF=None,
                lineup_SP1=None, lineup_SP2=None, lineup_SP3=None,
                lineup_SP4=None, lineup_SP5=None,
                lineup_RP1=None, lineup_RP2=None, lineup_RP3=None,
            )
            self.stdout.write('Cleared all rosters and lineups.')

        teams = list(Team.objects.all())
        if not teams:
            self.stdout.write(self.style.ERROR('No teams found.'))
            return

        # Fill each team up to per_team, pulling from unowned MLB players
        total_assigned = 0
        for team in teams:
            current = Player.objects.filter(team_assigned=team).count()
            needed = per_team - current
            if needed <= 0:
                continue

            qs = Player.objects.filter(team_assigned=None)
            if options['mlb_only']:
                qs = qs.filter(is_mlb=True)
            available = list(qs)
            random.shuffle(available)
            to_assign = available[:needed]

            for player in to_assign:
                player.team_assigned = team
                player.is_owned = True
                player.save()
                total_assigned += 1

        self.stdout.write(self.style.SUCCESS(
            f'Assigned {total_assigned} players across {len(teams)} teams '
            f'(target: {per_team} per team).'
        ))
