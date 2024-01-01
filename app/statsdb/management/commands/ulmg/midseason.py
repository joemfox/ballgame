import csv
import ujson as json
import os

from dateutil.parser import parse
from django.apps import apps
from django.db import connection
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Avg, Sum, Max, Min, Q
from django.conf import settings

from ulmg import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        # DO NOT RUN THIS UNTIL AFTER THE DRAFT IS OVER
        models.Player.objects.filter(is_2h_draft=True).update(is_2h_draft=False)
        models.Player.objects.filter(is_mlb_roster=True).update(is_mlb_roster=False)
        models.Player.objects.filter(is_aaa_roster=True).update(is_aaa_roster=False)
        models.Player.objects.filter(is_1h_c=True).update(
            is_mlb_roster=True, is_protected=True
        )
        models.Player.objects.filter(is_1h_p=True).update(
            is_mlb_roster=True, is_protected=True
        )
        models.Player.objects.filter(is_1h_pos=True).update(
            is_mlb_roster=True, is_protected=True
        )
        models.Player.objects.filter(is_reserve=True).update(is_protected=True)

        for p in models.DraftPick.objects.filter(
            year=settings.CURRENT_SEASON, season="midseason", draft_type="open"
        ):
            if p.player:
                p.player.is_2h_draft = True
                p.player.is_mlb_roster = True
                p.player.save()
