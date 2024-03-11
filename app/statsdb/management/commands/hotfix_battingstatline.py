import sys
from statsdb import models
from django.apps import apps
from django.db import connection
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        # statlines = models.BattingStatLine.objects.all()
        # for batter in statlines:
        #     if batter.player == None:
        #         player = models.Player.objects.all().filter(mlbam_id=batter.player_mlbam_id)
        #         if(len(player) > 0):
        #             batter.player = player.first()
        #     batter.save()
        statlines = models.PitchingStatLine.objects.all()
        for pitcher in statlines:
            # if pitcher.player == None:
            #     player = models.Player.objects.all().filter(mlbam_id=pitcher.player_mlbam_id)
            #     if(len(player) > 0):
            #         pitcher.player = player.first()
            pitcher.save()