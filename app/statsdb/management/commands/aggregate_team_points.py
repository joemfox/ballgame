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
        parser.add_argument("date", type=str)

    def handle(self, *args, **options):
        date = options['date']
        
        teams = models.Team.objects.all()
        for team in teams:
            agg = models.BattingStatLine.objects.all().filter(date = date).filter(fantasy_team=team).aggregate(games=Count("ab"), outs=Sum("outs"), bb=Sum("bb"), triples=Sum("triples"), h=Sum("h"), cycle=Count(Case(When(cycle=True,then=1))), doubles=Sum("doubles"), outfield_assists=Sum("outfield_assists"), cs=Sum("cs"), e=Sum("e"), gidp=Sum("gidp"), hr=Sum("hr"), r=Sum("r"), lob=Sum("lob"), po=Sum("po"), rl2o=Sum("rl2o"), rbi=Sum("rbi"), k_looking=Sum("k_looking"), k=Sum("k"), sb=Sum("sb"), FAN_outs = Sum("FAN_outs"), FAN_bb = Sum("FAN_bb"), FAN_triples = Sum("FAN_triples"), FAN_h = Sum("FAN_h"), FAN_cycle = Sum("FAN_cycle"), FAN_doubles = Sum("FAN_doubles"), FAN_outfield_assists = Sum("FAN_outfield_assists"), FAN_cs = Sum("FAN_cs"), FAN_e = Sum("FAN_e"), FAN_gidp = Sum("FAN_gidp"), FAN_hr = Sum("FAN_hr"), FAN_r = Sum("FAN_r"), FAN_lob = Sum("FAN_lob"), FAN_po = Sum("FAN_po"), FAN_rl2o = Sum("FAN_rl2o"), FAN_rbi = Sum("FAN_rbi"), FAN_k_looking = Sum("FAN_k_looking"), FAN_k = Sum("FAN_k"), FAN_sb = Sum("FAN_sb"))

            fan_total = sum(filter(None, [agg[f'FAN_{cat}'] for cat in settings.FAN_CATEGORIES_HIT]))
            agg["FAN_total"] = fan_total
            print(f'{team}: {fan_total}')

            stats, created = models.TeamBattingStatLine.objects.get_or_create(team=team,date=date)
            print(team, created)
            stats.team = team
            # stats.year = year
            # stats.date = datetime.datetime.now()
            for attr, value in agg.items():
                if attr not in ['active']:
                    # print(attr, value)
                    setattr(stats, attr, value)
            stats.save()

        for team in teams:
            agg = models.PitchingStatLine.objects.all().filter(date = date).filter(fantasy_team=team).aggregate(games=Count("ip"), ip=Sum("ip"), bb=Sum("bb"), er=Sum("er"), h=Sum("h"), bs=Count(Case(When(bs=True,then=1))), k=Sum("k"), hr=Sum("hr"), balks=Sum("balks"), e=Sum("e"), hb=Sum("hb"), bra=Sum("bra"), dpi=Sum("r"), wp=Sum("wp"), ir=Sum("ir"), irs=Sum("irs"), perfect_game=Count(Case(When(perfect_game=True,then=1))), no_hitter=Count(Case(When(no_hitter=True,then=1))), relief_loss=Count(Case(When(relief_loss=True,then=1))),FAN_ip = Sum("FAN_ip"), FAN_bb = Sum("FAN_bb"), FAN_er = Sum("FAN_er"), FAN_h = Sum("FAN_h"), FAN_perfect_game = Sum("FAN_perfect_game"), FAN_k = Sum("FAN_k"), FAN_hr = Sum("FAN_hr"), FAN_bs = Sum("FAN_bs"), FAN_balks = Sum("FAN_balks"), FAN_hb = Sum("FAN_hb"), FAN_bra = Sum("FAN_bra"), FAN_dpi = Sum("FAN_dpi"), FAN_e = Sum("FAN_e"), FAN_wp = Sum("FAN_wp"), FAN_ir = Sum("FAN_ir"), FAN_irs = Sum("FAN_irs"), FAN_no_hitter = Sum("FAN_no_hitter"), FAN_relief_loss = Sum("FAN_relief_loss"))
            
            fan_total = sum(filter(None, [agg[f'FAN_{cat}'] for cat in settings.FAN_CATEGORIES_PITCH]))
            agg["FAN_total"] = fan_total
            print(f'{team}: {fan_total}')

            stats, created = models.TeamPitchingStatLine.objects.get_or_create(team=team,date=date)
            print(team, created)
            stats.team = team
            # stats.year = year
            # stats.date = datetime.datetime.now()
            for attr, value in agg.items():
                if attr not in ['active']:
                    # print(attr, value)
                    setattr(stats, attr, value)
            stats.save()
            