
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import close_old_connections
import shutil
from tqdm import tqdm

from datetime import date, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("year", type=str)
        parser.add_argument("--workers", type=int, default=4,
                            help="Number of parallel day-workers (default: 4)")

    def handle(self, *args, **options):
        year = options["year"]

        start_date = date(int(year), 1, 1)
        end_date = date(int(year) + 1, 1, 1)
        day_strings = [d.strftime(settings.DATEFORMAT)
                       for d in daterange(start_date, end_date)]
        ncols = shutil.get_terminal_size().columns

        with tqdm(total=len(day_strings), desc="Aggregating teams", unit="day",
                  position=0, leave=True, ncols=ncols) as pbar:
            for day_str in day_strings:
                call_command('aggregate_team_points', day_str)
                pbar.update(1)

        call_command('aggregate_points', year)
