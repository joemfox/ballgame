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

from statsdb import models
import statsapi

import datetime
import pytz


class Command(BaseCommand):
    season = None
    games = []

    def add_arguments(self, parser):
        parser.add_argument("date", type=str)
        
    def handle(self, *args, **options):
        date = options.get("date", None)
        self.games = self.get_games(date)
        for (date,game_id) in self.games:
            self.load_game(date,game_id)

    def get_games(self,date):
        pacific = pytz.timezone("US/Pacific")
        now = datetime.datetime.now()
        if date:
            now = datetime.datetime.strptime(date,settings.DATEFORMAT)
        now = pacific.localize(now)
        start_time = datetime.datetime(now.year, now.month, now.day, 8, 0, 0, 0)
        start_time = pacific.localize(start_time)

        today = now.strftime("%m/%d/%Y")
        print(now)
        print(start_time)
        print(f"Loading game data for {today}")
        sched = [
            (now,d["game_id"]) for d in statsapi.schedule(start_date=today, end_date=today)
        ]
        return sched

    def load_game(self, date, game_id):
        game = statsapi.boxscore_data(game_id)
        batters = []
        pitchers = []
        batters += [g for g in game["awayBatters"] if g["personId"] != 0]
        batters += [g for g in game["homeBatters"] if g["personId"] != 0]
        pitchers += [g for g in game["awayPitchers"] if g["personId"] != 0]
        pitchers += [g for g in game["homePitchers"] if g["personId"] != 0]

        for batter in batters:
            statline = None
            try:
                statline = models.BattingStatLine.objects.get(id=f'{game_id}-{batter["personId"]}')
            except:
                statline = models.BattingStatLine()
                statline.id=f'{game_id}-{batter["personId"]}'   
            statline.date = date
            player = models.Player.objects.filter(mlbam_id=batter['personId'])
            if(len(player) == 1):
                statline.player = player[0]
            statline.last_name = batter['name']
            statline.ab = batter["ab"]
            statline.r = batter["r"]
            statline.h = batter["h"]
            statline.doubles = batter["doubles"]
            statline.triples = batter["triples"]
            statline.hr = batter["hr"]
            statline.rbi = batter["rbi"]
            statline.sb = batter["sb"]
            statline.bb = batter["bb"]
            statline.k = batter["k"]
            statline.lob = batter["lob"]
            statline.save()

        for pitcher in pitchers:
            statline = None
            try:
                statline = models.PitchingStatLine.objects.get(id=f'{game_id}-{batter["personId"]}')
            except:
                statline = models.PitchingStatLine()
                statline.id=f'{game_id}-{batter["personId"]}'   
            statline.date = date
            player = models.Player.objects.filter(mlbam_id=pitcher['personId'])
            if(len(player) == 1):
                statline.player = player[0]

            statline.last_name = pitcher['name']
            statline.ip = pitcher["ip"]
            statline.ph = pitcher["h"]
            statline.pr = pitcher["r"]
            statline.er = pitcher["er"]
            statline.pbb = pitcher["bb"]
            statline.pk = pitcher["k"]
            statline.phr = pitcher["hr"]
            statline.p = pitcher["p"]
            statline.s = pitcher["s"]
            statline.save()
