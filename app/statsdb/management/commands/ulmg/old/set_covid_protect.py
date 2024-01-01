import json
import time

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
import requests

from ulmg import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        models.Player.objects.filter(
            is_carded=False, is_owned=True, level__in=["A", "V"]
        ).update(covid_protected=True)
        for p in models.Player.objects.filter(
            is_carded=False, is_owned=True, level__in=["A", "V"]
        ):
            print(p)
