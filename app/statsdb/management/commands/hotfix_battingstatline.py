import sys
from statsdb import models
from django.apps import apps
from django.db import connection
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    statlines = models.BattingStatLine.objects.all()
    for batter in statlines:
        batter.save()