import csv
import json
import os
from decimal import Decimal

from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.apps import apps
from django.db import connection
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests

from statsdb import models, utils

from datetime import date, timedelta
import pytz

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