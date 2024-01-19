import csv
import json
import os
import time

from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.apps import apps
from django.db import connection
from django.db.models import Avg, Sum, Count
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests
import urllib3


class Command(BaseCommand):
    def handle(self, *args, **options):
        urllib3.disable_warnings()
        year = settings.CURRENT_SEASON
        url = f"https://www.fangraphs.com/api/tools/free-agent-tracker/v2/free-agents?season={year}"

        r = requests.get(url, verify=False)
        print(r.status_code, url)
        if r.status_code == 200:

            roster = r.json()            
            with open(f"data/rosters/free_agents.json", "w") as writefile:
                writefile.write(json.dumps(roster))