"""
Run once when preparing a new season (can be run during offseason/preseason).
- Clears all player roster assignments (team_assigned, is_fantasy_roster, is_aaa_roster, is_35man_roster)
- Creates empty SeasonBattingStatLine / SeasonPitchingStatLine records (all zeros)
  for every player so they appear on the leaderboard from day one.

Existing season stat records are left untouched (get_or_create).
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from statsdb import models


class Command(BaseCommand):
    help = "Clear rosters and seed zero-stat season records for all players for the current season"

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=None,
            help='Season year (defaults to CURRENT_SEASON)',
        )

    def handle(self, *args, **options):
        year = options['year'] or settings.CURRENT_SEASON

        # Clear all lineup slots
        LINEUP_SLOTS = [
            'lineup_C', 'lineup_1B', 'lineup_2B', 'lineup_SS', 'lineup_3B',
            'lineup_OF1', 'lineup_OF2', 'lineup_OF3', 'lineup_OF4', 'lineup_OF5',
            'lineup_UTIL', 'lineup_DH',
            'lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5',
            'lineup_RP1', 'lineup_RP2', 'lineup_RP3',
        ]
        models.Lineup.objects.update(**{slot: None for slot in LINEUP_SLOTS})
        self.stdout.write(f"Cleared all lineup slots.")

        # Clear all roster assignments
        cleared = models.Player.objects.filter(team_assigned__isnull=False).update(
            team_assigned=None,
            is_fantasy_roster=False,
            is_aaa_roster=False,
            is_35man_roster=False,
        )
        self.stdout.write(f"Cleared roster assignments for {cleared} players.")

        # Seed zero-stat season records
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
