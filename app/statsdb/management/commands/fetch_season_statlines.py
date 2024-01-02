
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from datetime import date, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("year", type=str)

    def handle(self, *args, **options):
        year = options.get("year", None)

        start_date = date(int(year),1,1)
        end_date = date(int(year)+1,1,1)
        for day in daterange(start_date,end_date):
            call_command('realtime_update',day.strftime(settings.DATEFORMAT))