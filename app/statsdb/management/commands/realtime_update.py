import sys
import json
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
    
    def count_rl2o(self,play):
        if play['result']['isOut'] and play['count']['outs'] == 3:
            rsp = [r for r in play['runners'] if r['movement']['originBase'] in ['2B','3B'] and r['movement']['end'] not in ['score'] and r['details']['eventType'] not in ['wild_pitch','passed_ball']]
            return len(rsp)
        else: return 0


    def load_game(self, date, game_id):
        box = statsapi.boxscore_data(game_id)
        pbp = statsapi.get('game_playByPlay',{'gamePk':game_id})
        # with open(f'data/test/{game_id}.json','w') as writefile:
        #     writefile.write(json.dumps(pbp))
        batters = []
        pitchers = []
        batters += [g for g in box["awayBatters"] if g["personId"] != 0]
        batters += [g for g in box["homeBatters"] if g["personId"] != 0]
        pitchers += [g for g in box["awayPitchers"] if g["personId"] != 0]
        pitchers += [g for g in box["homePitchers"] if g["personId"] != 0]

        for batter in batters:
            batting_plays = [p for p in pbp['allPlays'] if p['matchup']['batter']['id'] == batter['personId']]

            running_plays = [[runner for runner in p['runners'] if runner['details']['runner']['id'] == batter['personId']][0] for p in pbp['allPlays'] if len([r for r in p['runners'] if r['details']['runner']['id'] == batter['personId'] and r['movement']['originBase'] is not None]) > 0]

            fielding_plays = []

            for play in pbp['allPlays']:
                for runner in play['runners']:
                    for fielder in runner['credits']:
                        if fielder['player']['id'] == batter['personId']:
                            fielding_plays.append(fielder)

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
            statline.player_mlbam_id = batter['personId']
                
            statline.last_name = batter['name']
            statline.ab = batter["ab"]
            statline.r = batter["r"]
            statline.h = batter["h"]
            statline.outs = int(batter['ab']) - int(batter['h'])
            statline.doubles = batter["doubles"]
            statline.triples = batter["triples"]
            statline.hr = batter["hr"]
            statline.rbi = batter["rbi"]
            statline.sb = batter["sb"]
            statline.bb = batter["bb"]
            statline.k = batter["k"]
            
            singles = int(statline.h) - int(statline.hr) - int(statline.triples) - int(statline.doubles)
            statline.cycle = all(h > 0 for h in [int(s) for s in [statline.doubles,statline.triples,statline.hr,singles]])
            statline.rl2o = sum([self.count_rl2o(play) for play in batting_plays])
            statline.gidp = len([p for p in batting_plays if p['result']['eventType'] == 'grounded_into_double_play'])
            statline.po = len([play for play in running_plays if play['details']['eventType'] is not None and 'pickoff' in play['details']['eventType']])
            statline.cs = len([play for play in running_plays if play['details']['eventType'] is not None and 'caught_stealing' in play['details']['eventType'] and 'pickoff' not in play['details']['eventType']])
            statline.outfield_assists = len([play for play in fielding_plays if play['credit'] == 'f_assist_of'])
            statline.e = len([play for play in fielding_plays if 'error' in play['credit']])
            statline.k_looking = len([play for play in batting_plays if 'called out on strikes' in play['result']['description']])
            
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
