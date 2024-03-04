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
        
        for duplicates in models.SeasonBattingStatline.objects.filter(year=year).values('player').annotate(
            records=Count('player')
        ).filter(records__gt=1):
            for line in models.SeasonBattingStatline.objects.filter(year=year,player=duplicates["player"])[1:]:
                line.delete()
            