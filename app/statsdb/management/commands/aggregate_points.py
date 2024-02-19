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
        
        players = models.Player.objects.all()
        for player in players:
            print(player)
            agg = models.BattingStatLine.objects.all().filter(player=player).filter(date__year = year).aggregate(games=Count("ab"), outs=Sum("outs"), bb=Sum("bb"), triples=Sum("triples"), hits=Sum("h"), cycle=Count(Case(When(cycle=True,then=1))), doubles=Sum("doubles"), outfield_assists=Sum("outfield_assists"), cs=Sum("cs"), e=Sum("e"), gidp=Sum("gidp"), hr=Sum("hr"), r=Sum("r"), lob=Sum("lob"), po=Sum("po"), rl2o=Sum("rl2o"), rbi=Sum("rbi"), k_looking=Sum("k_looking"), k=Sum("k"), sb=Sum("sb"), FAN_outs = Sum("FAN_outs"), FAN_bb = Sum("FAN_bb"), FAN_triples = Sum("FAN_triples"), FAN_hits = Sum("FAN_hits"), FAN_cycle = Sum("FAN_cycle"), FAN_doubles = Sum("FAN_doubles"), FAN_outfield_assists = Sum("FAN_outfield_assists"), FAN_cs = Sum("FAN_cs"), FAN_e = Sum("FAN_e"), FAN_gidp = Sum("FAN_gidp"), FAN_hr = Sum("FAN_hr"), FAN_r = Sum("FAN_r"), FAN_lob = Sum("FAN_lob"), FAN_po = Sum("FAN_po"), FAN_rl2o = Sum("FAN_rl2o"), FAN_rbi = Sum("FAN_rbi"), FAN_k_looking = Sum("FAN_k_looking"), FAN_k = Sum("FAN_k"), FAN_sb = Sum("FAN_sb"))

            stats = models.SeasonBattingStatline()
            stats.player = player
            stats.player_mlbam_id = player.mlbam_id if player.mlbam_id else player.fg_id
            stats.year = year
            stats.date = datetime.datetime.now()
            for attr, value in agg.items():
                if attr not in ['active']:
                    print(attr, value)
                    setattr(stats, attr, value)
            stats.save()
            