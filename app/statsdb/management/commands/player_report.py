import sys
import datetime
from statsdb import models
from django.apps import apps
from django.db import connection
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Sum, Count, Case, When

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("year", type=str)

    def handle(self, *args, **options):
        year = options.get("year", None)
        print('BEST WORST PLAYERS')
        queryset = models.SeasonBattingStatLine.objects.all().filter(year=year).order_by('-FAN_total')[:25]
        for line in queryset:
            print(f'{getattr(line,"player")}: {getattr(line,"FAN_total")}')
        
        print('\nWORST WORST PLAYERS')
        queryset = models.SeasonBattingStatLine.objects.all().filter(year=year).order_by('FAN_total')[:25]
        for line in queryset:
            print(f'{getattr(line,"player")}: {getattr(line,"FAN_total")}')