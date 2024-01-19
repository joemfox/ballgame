
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import shutil
import os
from tqdm import tqdm

from datetime import date, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("year", type=str)

    def handle(self, *args, **options):
        year = options.get("year", None)

        start_date = date(int(year),4,1)
        end_date = date(int(year)+1,1,1)
        os.system('clear')
        terminal_size = shutil.get_terminal_size()
        for day in tqdm(daterange(start_date,end_date), desc="Loading season", ncols=terminal_size.columns, position=terminal_size.lines - 20, total=int((end_date - start_date).days), unit="day", leave=False):

            print(f'\033[{terminal_size.lines}B')
            call_command('realtime_update',day.strftime(settings.DATEFORMAT),terminal_size.lines,terminal_size.columns,False)