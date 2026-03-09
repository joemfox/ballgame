"""
Wipes all application data from the database while preserving schema,
users, and Django system tables.

Usage:
    python manage.py clear_data          # prompts for confirmation
    python manage.py clear_data --yes    # skips confirmation
"""
from django.core.management.base import BaseCommand
from statsdb import models


MODELS_TO_CLEAR = [
    models.DraftPick,
    models.Draft,
    models.RosterSnapshot,
    models.BattingStatLine,
    models.PitchingStatLine,
    models.SeasonBattingStatLine,
    models.SeasonPitchingStatLine,
    models.TeamBattingStatLine,
    models.TeamPitchingStatLine,
    models.Lineup,
    models.Team,
    models.Player,
]


class Command(BaseCommand):
    help = 'Delete all application data (players, stats, teams, drafts). Preserves users and Django system tables.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        if not options['yes']:
            confirm = input(
                'This will permanently delete ALL application data. Type "yes" to confirm: '
            )
            if confirm.strip().lower() != 'yes':
                self.stdout.write('Aborted.')
                return

        for model in MODELS_TO_CLEAR:
            count, _ = model.objects.all().delete()
            self.stdout.write(f'  Deleted {count:>6} rows from {model.__name__}')

        self.stdout.write(self.style.SUCCESS('Done.'))
