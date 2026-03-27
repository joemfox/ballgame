import datetime
from django.core.management.base import BaseCommand, CommandError
from statsdb import models


class Command(BaseCommand):
    help = 'Backfill missing RosterSnapshots for a date using fantasy_team from existing statlines.'

    def add_arguments(self, parser):
        parser.add_argument('date', type=str, help='Date in YYYY-MM-DD format')

    def handle(self, *args, **options):
        date_str = options['date']
        try:
            snap_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise CommandError(f'Invalid date format: {date_str}. Use YYYY-MM-DD.')

        existing = set(
            models.RosterSnapshot.objects.filter(date=snap_date)
            .values_list('player_id', flat=True)
        )

        created = 0
        skipped = 0

        batting = (
            models.BattingStatLine.objects
            .filter(date=snap_date, fantasy_team__isnull=False, player__isnull=False)
            .select_related('player', 'fantasy_team')
        )
        for sl in batting:
            if sl.player_id in existing:
                skipped += 1
                continue
            models.RosterSnapshot.objects.create(
                date=snap_date,
                player=sl.player,
                team=sl.fantasy_team,
            )
            existing.add(sl.player_id)
            created += 1

        pitching = (
            models.PitchingStatLine.objects
            .filter(date=snap_date, fantasy_team__isnull=False, player__isnull=False)
            .select_related('player', 'fantasy_team')
        )
        for sl in pitching:
            if sl.player_id in existing:
                skipped += 1
                continue
            models.RosterSnapshot.objects.create(
                date=snap_date,
                player=sl.player,
                team=sl.fantasy_team,
            )
            existing.add(sl.player_id)
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {created} snapshot(s), skipped {skipped} already-existing for {snap_date}'
        ))
