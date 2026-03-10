from django.core.management.base import BaseCommand

from statsdb import models


class Command(BaseCommand):
    help = 'Set fantasy_team on all statlines for a year to the player\'s current team_assigned (testing only)'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)

    def handle(self, *args, **options):
        year = options['year']

        players = models.Player.objects.filter(team_assigned__isnull=False).select_related('team_assigned')
        self.stdout.write(f'{players.count()} owned players')

        bat_total = 0
        pit_total = 0
        for player in players:
            n = models.BattingStatLine.objects.filter(player=player, date__year=year).update(fantasy_team=player.team_assigned)
            bat_total += n
            n = models.PitchingStatLine.objects.filter(player=player, date__year=year).update(fantasy_team=player.team_assigned)
            pit_total += n

        self.stdout.write(f'Updated {bat_total} batting + {pit_total} pitching statlines')
        self.stdout.write(self.style.SUCCESS('Done.'))
