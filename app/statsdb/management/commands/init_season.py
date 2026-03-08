"""
Run once when switching CURRENT_SEASON_TYPE to "inseason".
Creates empty SeasonBattingStatLine / SeasonPitchingStatLine records (all zeros)
for every player so they appear on the leaderboard from day one.

Existing records are left untouched (get_or_create).
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from statsdb import models, utils


class Command(BaseCommand):
    help = "Seed zero-stat season records for all players for the current season"

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=None,
            help='Season year (defaults to CURRENT_SEASON)',
        )

    def handle(self, *args, **options):
        year = options['year'] or settings.CURRENT_SEASON
        players = models.Player.objects.all()
        bat_created = pit_created = 0

        for player in players:
            mlbam_id = player.mlbam_id or player.fg_id
            pos = player.position or ''
            is_pitcher = 'P' in pos
            is_batter = pos != 'P'

            if is_batter:
                _, created = models.SeasonBattingStatLine.objects.get_or_create(
                    player=player,
                    year=year,
                    defaults={'player_mlbam_id': mlbam_id, 'FAN_total': 0},
                )
                if created:
                    bat_created += 1

            if is_pitcher:
                _, created = models.SeasonPitchingStatLine.objects.get_or_create(
                    player=player,
                    year=year,
                    defaults={'player_mlbam_id': mlbam_id, 'FAN_total': 0},
                )
                if created:
                    pit_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Season {year}: created {bat_created} batting and {pit_created} pitching records."
        ))
