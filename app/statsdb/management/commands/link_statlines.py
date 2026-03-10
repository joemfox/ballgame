from django.core.management import call_command
from django.core.management.base import BaseCommand

from statsdb import models


class Command(BaseCommand):
    help = 'Link orphaned statlines to Player records by mlbam_id, then re-aggregate season stats'

    def handle(self, *args, **options):
        # Build a lookup of mlbam_id -> Player for all players that have one
        player_map = {
            p.mlbam_id: p
            for p in models.Player.objects.filter(mlbam_id__isnull=False).exclude(mlbam_id='')
        }
        self.stdout.write(f'{len(player_map)} players with mlbam_id')

        affected_years = set()

        # BattingStatLine
        qs = models.BattingStatLine.objects.filter(player__isnull=True).exclude(player_mlbam_id='')
        bat_total = qs.count()
        bat_linked = 0
        for sl in qs.iterator():
            p = player_map.get(str(sl.player_mlbam_id))
            if p:
                sl.player = p
                sl.save(update_fields=['player'])
                bat_linked += 1
                if sl.date:
                    affected_years.add(sl.date.year)
        self.stdout.write(f'BattingStatLine: linked {bat_linked}/{bat_total}')

        # PitchingStatLine
        qs = models.PitchingStatLine.objects.filter(player__isnull=True).exclude(player_mlbam_id='')
        pit_total = qs.count()
        pit_linked = 0
        for sl in qs.iterator():
            p = player_map.get(str(sl.player_mlbam_id))
            if p:
                sl.player = p
                sl.save(update_fields=['player'])
                pit_linked += 1
                if sl.date:
                    affected_years.add(sl.date.year)
        self.stdout.write(f'PitchingStatLine: linked {pit_linked}/{pit_total}')

        if not affected_years:
            self.stdout.write('No statlines linked — nothing to aggregate.')
            return

        for year in sorted(affected_years):
            self.stdout.write(f'Aggregating {year}...')
            call_command('aggregate_points', str(year))

        self.stdout.write(self.style.SUCCESS('Done.'))
