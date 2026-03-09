from functools import reduce
import operator

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import F, Value
from django.db.models.functions import Coalesce

from statsdb import models
from statsdb.settings import FAN_CATEGORIES_HIT, FAN_CATEGORIES_PITCH


def build_sum_expr(categories):
    """Build a DB expression that sums Coalesce(FAN_cat, 0) for each category."""
    terms = [Coalesce(F(f'FAN_{cat}'), Value(0.0)) for cat in categories]
    return reduce(operator.add, terms)


class Command(BaseCommand):
    help = 'Recalculate all FAN columns for game-level and season stat lines'

    def handle(self, *args, **options):
        # Step 1: force Postgres to recompute stored generated columns by doing a
        # no-op UPDATE that touches every row, then set FAN_total from the fresh values.
        # PostgreSQL recomputes STORED GENERATED columns on every UPDATE before
        # evaluating the SET clause, so the sum expression reads the new values.

        hit_expr = build_sum_expr(FAN_CATEGORIES_HIT)
        n = models.BattingStatLine.objects.update(FAN_total=hit_expr)
        self.stdout.write(f'Updated {n} BattingStatLine records')

        pitch_expr = build_sum_expr(FAN_CATEGORIES_PITCH)
        n = models.PitchingStatLine.objects.update(FAN_total=pitch_expr)
        self.stdout.write(f'Updated {n} PitchingStatLine records')

        # Step 2: re-aggregate season stat lines for every year that has game data.
        years = set()
        years.update(
            models.BattingStatLine.objects.values_list('date__year', flat=True).distinct()
        )
        years.update(
            models.PitchingStatLine.objects.values_list('date__year', flat=True).distinct()
        )

        for year in sorted(years):
            self.stdout.write(f'Aggregating season stats for {year}...')
            call_command('aggregate_points', str(year))

        self.stdout.write(self.style.SUCCESS('Done.'))
