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
from tqdm import tqdm


class Command(BaseCommand):
    season = None
    games = []

    def add_arguments(self, parser):
        parser.add_argument("date", type=str)
        parser.add_argument("terminal_height", type=int,default=32,)
        parser.add_argument("terminal_width", type=int, default=40)
        parser.add_argument("overwrite",type=bool, default=True)
        
    def handle(self, *args, **options):
        date = options['date']
        terminal_height = options['terminal_height']
        terminal_width = options['terminal_width']
        overwrite = options['overwrite']
        self.games = self.get_games(date)


        for (date, game_id) in tqdm(self.games, desc="Loading games", ncols=terminal_width, position=terminal_height - 16, total=len(self.games), unit="game", leave=False):
            self.load_game(date, game_id, overwrite)
            print(f"\033[F\033[K", end="")

    def get_games(self,date):
        pacific = pytz.timezone("US/Pacific")
        now = datetime.datetime.now()
        if date:
            now = datetime.datetime.strptime(date,settings.DATEFORMAT)
        now = pacific.localize(now)
        start_time = datetime.datetime(now.year, now.month, now.day, 8, 0, 0, 0)
        start_time = pacific.localize(start_time)

        today = now.strftime("%m/%d/%Y")
        sched = [
            (now,d["game_id"]) for d in statsapi.schedule(start_date=today, end_date=today)
        ]
        return sched
    
    def count_rl2o(self,play):
        if play['result']['isOut'] and play['count']['outs'] == 3:
            rsp = [r for r in play['runners'] if r['movement']['originBase'] in ['2B','3B'] and r['movement']['end'] not in ['score'] and r['details']['eventType'] not in ['wild_pitch','passed_ball']]
            return len(rsp)
        else: return 0


    def load_game(self, date, game_id, overwrite):
        try:
            box = statsapi.boxscore_data(game_id)
        except KeyError:
            print(f'error parsing game {game_id}, skipping')
            return
        pbp = statsapi.get('game_playByPlay',{'gamePk':game_id})
        # with open(f'data/test/pbp/box_{game_id}.json','w') as writefile:
        #     writefile.write(json.dumps(pbp))
        batters = []
        pitchers = []
        batters += [g for g in box["awayBatters"] if g["personId"] != 0]
        batters += [g for g in box["homeBatters"] if g["personId"] != 0]
        awayPitchers = [g for g in box["awayPitchers"] if g["personId"] != 0]
        for i, p in enumerate(awayPitchers):
            if i != 0:
                p['is_reliever'] = True
            else:
                p['is_reliever'] = False
        homePitchers = [g for g in box["homePitchers"] if g["personId"] != 0]
        for i, p in enumerate(homePitchers):
            if i != 0:
                p['is_reliever'] = True
            else:
                p['is_reliever'] = False

        pitchers += awayPitchers
        pitchers += homePitchers

        for batter in batters:
            batting_plays = [p for p in pbp['allPlays'] if p['matchup']['batter']['id'] == batter['personId']]

            running_plays = [[runner for runner in p['runners'] if runner['details']['runner']['id'] == batter['personId']][0] for p in pbp['allPlays'] if len([r for r in p['runners'] if r['details']['runner']['id'] == batter['personId'] and r['movement']['originBase'] is not None]) > 0]

            fielding_plays = []

            try:
                for play in pbp['allPlays']:
                    for runner in play['runners']:
                        for fielder in runner['credits']:
                            if fielder['player']['id'] == batter['personId']:
                                fielding_plays.append(fielder)
            except:
                pass

            statline = None
            try:
                statline = models.BattingStatLine.objects.get(id=f'{game_id}-{batter["personId"]}')
            except:
                # print('statline not found, creating new one',file=sys.stderr)
                statline = models.BattingStatLine()
                statline.id=f'{game_id}-{batter["personId"]}'   
            statline.date = date
            
            player = models.Player.objects.all().filter(mlbam_id=batter["personId"])
            if(len(player) > 0):
                statline.player = player.first()
                try:
                    fantasy_team = getattr(player.first(),'team_assigned')
                    if fantasy_team is not None:
                        statline.fantasy_team = fantasy_team
                        # print(f'{player.first().name}: {fantasy_team}')
                except AttributeError:
                    # print('fantasy team not found',file=sys.stderr)
                    pass

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
            # print(statline,file=sys.stderr)
            statline.save()

        def is_qs(pitcher, line):
            return not pitcher['is_reliever'] and Decimal(line['earnedRuns']) <= 3 and Decimal(line['inningsPitched']) >= 6
        def is_pg(line,plays):
            return len(plays) == 27 and line['inningsPitched'] == '9.0' and line['runs'] == 0 and line['hits'] == 0 and line['baseOnBalls'] == 0
        def is_nh(line,plays):
            return line['inningsPitched'] == '9.0'and line['hits'] == 0
        def get_inherited(pitcher, box):
            for entry in box['gameBoxInfo']:
                if entry['label'] == 'Inherited runners-scored':
                    pitchers = entry['value'].split(';')
                    for p in pitchers:
                        if pitcher['namefield'] in p:
                            return p.replace('.','').split(' ')[-1].split('-')
            return [0,0]
        
        def is_relief_loss(pitcher):
            return pitcher['is_reliever'] and 'L' in pitcher['note']
        for pitcher in pitchers:
            pitching_line = box['home']['players'][f'ID{pitcher["personId"]}']['stats']['pitching'] if pitcher in box['homePitchers'] else box['away']['players'][f'ID{pitcher["personId"]}']['stats']['pitching']

            pitching_plays = [play for play in pbp['allPlays'] if play['matchup']['pitcher']['id'] == pitcher["personId"]]

            fielding_plays = []

            try:
                for play in pbp['allPlays']:
                    for runner in play['runners']:
                        for fielder in runner['credits']:
                            if fielder['player']['id'] == pitcher['personId']:
                                fielding_plays.append(fielder)
            except:
                pass

            pitching_events = [[event['details'] for event in play['playEvents']] for play in pitching_plays]      
            pitching_events = [[event['eventType'] for event in events if 'eventType' in event.keys()] for events in pitching_events]
            pitching_events = [item for sublist in pitching_events for item in sublist]



            statline = None
            statline = models.PitchingStatLine.objects.filter(statline_id=f'{game_id}-{pitcher["personId"]}')
            if len(statline) > 0:
                statline = statline[0]
            else:
                print('statline not found, creating new one',file=sys.stderr)
                statline = models.PitchingStatLine()
                statline.statline_id=f'{game_id}-{pitcher["personId"]}'   
                
            statline.date = date
            statline.save()

            player = models.Player.objects.all().filter(mlbam_id=pitcher["personId"])
            if(len(player) > 0):
                setattr(statline,'player',player.first())
                try:
                    fantasy_team = getattr(player.first(),'team_assigned')
                    if fantasy_team is not None:
                        statline.fantasy_team = fantasy_team
                        print(f'{player.first().name}: {fantasy_team}')
                except AttributeError:
                    # print('fantasy team not found',file=sys.stderr)
                    pass

            setattr(statline, 'player_mlbam_id', pitcher['personId'])
            setattr(statline, 'last_name', pitcher['name'])
            setattr(statline, 'ip', Decimal(pitcher["ip"]))
            setattr(statline, 'h', pitcher["h"])
            setattr(statline, 'r', pitcher["r"])
            setattr(statline, 'er', pitcher["er"])
            setattr(statline, 'bb', pitcher["bb"])
            setattr(statline, 'k', pitcher["k"])
            setattr(statline, 'hr', pitcher["hr"])
            setattr(statline, 'bs', pitching_line['blownSaves'])
            setattr(statline, 'bf', len(pitching_plays))
            setattr(statline, 'balks',len(list(filter(lambda x: x == 'balk',pitching_events))))
            setattr(statline,'hb',len([p for p in pitching_plays if p['result']['eventType'] == 'hit_by_pitch']))
            setattr(statline,'dpi',len([p for p in pitching_plays if 'double_play' in p['result']['eventType']]))
            setattr(statline,'bra',sum((int(statline.bb), int(statline.h), int(statline.hb))))
            setattr(statline,'e',len([play for play in fielding_plays if 'error' in play['credit']]))
            setattr(statline, 'wp',len(list(filter(lambda x: x == 'wild_pitch',pitching_events))))
            setattr(statline,'ir',int(get_inherited(pitcher,box)[0]))
            setattr(statline,'irs',int(get_inherited(pitcher,box)[0]) -int(get_inherited(pitcher,box)[1]))
            setattr(statline, 'quality_start',is_qs(pitcher,pitching_line))
            setattr(statline, 'perfect_game',is_pg(pitching_line, pitching_plays))
            setattr(statline, 'no_hitter',is_nh(pitching_line, pitching_plays))
            setattr(statline,'relief_loss',is_relief_loss(pitcher))
            print(statline)
            statline.save()
