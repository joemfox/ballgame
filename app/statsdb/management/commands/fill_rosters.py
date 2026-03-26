"""
Fill lineup slots with randomly assigned unowned players.

Usage:
    python manage.py fill_rosters              # fill all empty slots (MLB players only)
    python manage.py fill_rosters --clear      # clear rosters first, then fill
    python manage.py fill_rosters --all-players  # include non-MLB players
"""
import random
from django.core.management.base import BaseCommand
from statsdb.models import Player, Team, Lineup

# Maps each lineup slot to the position values that can fill it.
# Matches positions stored in Player.positions (ArrayField).
SLOT_POSITIONS = {
    'lineup_C':    ['C'],
    'lineup_1B':   ['1B'],
    'lineup_2B':   ['2B', 'IF', 'IN'],
    'lineup_SS':   ['SS', 'IF', 'IN'],
    'lineup_3B':   ['3B', 'IF', 'IN'],
    'lineup_OF1':  ['LF', 'CF', 'RF', 'OF'],
    'lineup_OF2':  ['LF', 'CF', 'RF', 'OF'],
    'lineup_OF3':  ['LF', 'CF', 'RF', 'OF'],
    'lineup_OF4':  ['LF', 'CF', 'RF', 'OF'],
    'lineup_OF5':  ['LF', 'CF', 'RF', 'OF'],
    'lineup_DH':   ['DH'],
    'lineup_UTIL': ['C', '1B', '2B', 'SS', '3B', 'LF', 'CF', 'RF', 'OF', 'IF', 'IN', 'DH'],
    'lineup_SP1':  ['SP'],
    'lineup_SP2':  ['SP'],
    'lineup_SP3':  ['SP'],
    'lineup_SP4':  ['SP'],
    'lineup_SP5':  ['SP'],
    'lineup_RP1':  ['RP'],
    'lineup_RP2':  ['RP'],
    'lineup_RP3':  ['RP'],
}


class Command(BaseCommand):
    help = 'Fill lineup slots with randomly assigned unowned players'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help='Clear all existing roster assignments first')
        parser.add_argument('--all-players', action='store_true',
                            help='Include non-MLB players (default: MLB only)')

    def handle(self, *args, **options):
        if options['clear']:
            Player.objects.update(team_assigned=None, is_owned=False)
            Lineup.objects.update(
                lineup_C=None, lineup_1B=None, lineup_2B=None,
                lineup_SS=None, lineup_3B=None,
                lineup_OF1=None, lineup_OF2=None, lineup_OF3=None,
                lineup_OF4=None, lineup_OF5=None,
                lineup_DH=None, lineup_UTIL=None,
                lineup_SP1=None, lineup_SP2=None, lineup_SP3=None,
                lineup_SP4=None, lineup_SP5=None,
                lineup_RP1=None, lineup_RP2=None, lineup_RP3=None,
            )
            self.stdout.write('Cleared all rosters and lineups.')
            return
        
        teams = list(Team.objects.all())
        if not teams:
            self.stdout.write(self.style.ERROR('No teams found.'))
            return

        total_assigned = 0
        for team in teams:
            lineup, _ = Lineup.objects.get_or_create(lineup_team=team)
            lineup_dirty = False

            for slot, positions in SLOT_POSITIONS.items():
                if getattr(lineup, slot + '_id') is not None:
                    continue  # slot already filled

                qs = Player.objects.filter(team_assigned=None, positions__overlap=positions)
                if not options['all_players']:
                    qs = qs.filter(level="MLB")
                candidates = list(qs)
                if not candidates:
                    continue

                player = random.choice(candidates)
                setattr(lineup, slot, player)
                player.team_assigned = team
                player.is_owned = True
                player.save()
                lineup_dirty = True
                total_assigned += 1

            if lineup_dirty:
                lineup.save()

        self.stdout.write(self.style.SUCCESS(
            f'Assigned {total_assigned} players across {len(teams)} teams.'
        ))
