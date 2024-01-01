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

from ulmg import models, utils


class Command(BaseCommand):
    def set_carded(self, *args, **options):
        season = get_current_season()

        if not options.get("dry_run", None):
            models.Player.objects.all().update(is_carded=False)
            models.Player.objects.filter(
                stats__current__year=season, stats__current__type="majors"
            ).update(is_carded=True)
        else:
            print(models.Player.objects.filter(stats__current__year=season).count())


    def reset_rosters(self, *args, **options):
        if not options.get("dry_run", None):
            models.Player.objects.filter(is_mlb_roster=True).update(is_mlb_roster=False)
            models.Player.objects.filter(is_aaa_roster=True).update(is_aaa_roster=False)
            models.Player.objects.filter(is_35man_roster=True).update(is_35man_roster=False)
            models.Player.objects.filter(is_1h_c=True).update(is_1h_c=False)
            models.Player.objects.filter(is_1h_p=True).update(is_1h_p=False)
            models.Player.objects.filter(is_1h_pos=True).update(is_1h_pos=False)
            models.Player.objects.filter(is_reserve=True).update(is_reserve=False)

            models.Player.objects.filter(is_2h_c=True).update(is_2h_c=False)
            models.Player.objects.filter(is_2h_p=True).update(is_2h_p=False)
            models.Player.objects.filter(is_2h_pos=True).update(is_2h_pos=False)
            models.Player.objects.filter(is_2h_draft=True).update(is_2h_draft=False)

            # Unprotect all V and A players prior to the 35-man roster.
            models.Player.objects.filter(is_owned=True, level__in=["A", "V"]).update(
                is_protected=False
            )
            models.Player.objects.filter(
                is_owned=True, is_carded=False, level__in=["A", "V"]
            ).update(is_protected=True)


    def load_career_hit(self, *args, **options):
        """
        https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=250&type=8&season=2022&month=0&season1=2000&ind=0&team=0&rost=0&age=&filter=&players=0&startdate=&enddate=&page=1_5000
        """

        hostname = get_hostname()
        scriptname = get_scriptname()
        timestamp = generate_timestamp()

        print(f"{timestamp}\tcareer\tload_career_hit")

        with open("data/career/hit.csv", "r") as readfile:
            players = csv.DictReader(readfile)
            for row in [dict(z) for z in players]:
                try:
                    p = models.Player.objects.get(fg_id=row["playerid"])
                    if not p.stats.get("career", None):
                        p.stats["career"] = {}
                        p.stats["career"]["pa"] = None

                    p.stats["career"]["year"] = "career"
                    p.stats["career"]["type"] = "majors"
                    p.stats["career"]["timestamp"] = timestamp
                    p.stats["career"]["level"] = "mlb"
                    p.stats["career"]["side"] = "pitch"
                    p.stats["career"]["script"] = scriptname
                    p.stats["career"]["host"] = hostname
                    p.stats["career"][
                        "slug"
                    ] = f"{ p.stats['career']['year']}_{ p.stats['career']['type']}"

                    p.stats["career"]["pa"] = int(row["PA"])

                    if not options.get("dry_run", None):
                        p.save()

                except:
                    pass


    def load_career_pitch(self, *args, **options):
        """
        https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=30&type=8&season=2022&month=0&season1=2000&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=&enddate=&page=1_5000
        """

        hostname = get_hostname()
        scriptname = get_scriptname()
        timestamp = generate_timestamp()

        print(f"{timestamp}\tcareer\tload_career_pitch")

        with open("data/career/pitch.csv", "r") as readfile:
            players = csv.DictReader(readfile)
            for row in [dict(z) for z in players]:
                try:
                    p = models.Player.objects.get(fg_id=row["playerid"])
                    if not p.stats.get("career", None):
                        p.stats["career"] = {}

                        p.stats["career"]["gs"] = None
                        p.stats["career"]["g"] = None
                        p.stats["career"]["ip"] = None

                    p.stats["career"]["year"] = "career"
                    p.stats["career"]["type"] = "majors"
                    p.stats["career"]["timestamp"] = timestamp
                    p.stats["career"]["level"] = "mlb"
                    p.stats["career"]["side"] = "pitch"
                    p.stats["career"]["script"] = scriptname
                    p.stats["career"]["host"] = hostname
                    p.stats["career"][
                        "slug"
                    ] = f"{ p.stats['career']['year']}_{ p.stats['career']['type']}"

                    p.stats["career"]["gs"] = int(row["GS"])
                    p.stats["career"]["g"] = int(row["G"])
                    p.stats["career"]["ip"] = int(row["IP"].split(".")[0])

                    if not options.get("dry_run", None):
                        p.save()

                except:
                    pass


    def set_levels(self, *args, **options):
        print("--------- STARTERS B > A ---------")
        for p in models.Player.objects.filter(
            level="B", position="P", stats__career__gs__gte=21
        ):
            p.level = "A"
            print(p)
            if not options.get("dry_run", None):
                p.save()

        print("--------- RELIEVERS B > A ---------")
        for p in models.Player.objects.filter(
            level="B", position="P", stats__career__g__gte=31
        ):
            p.level = "A"
            print(p)
            if not options.get("dry_run", None):
                p.save()
        print("--------- SWINGMEN B > A ---------")
        for p in models.Player.objects.filter(
            level="B", position="P", stats__career__g__gte=40, stats__career__gs__gte=15
        ):
            p.level = "A"
            print(p)
            if not options.get("dry_run", None):
                p.save()

        print("--------- HITTERS B > A ---------")
        for p in models.Player.objects.filter(level="B", stats__career__pa__gte=300):
            p.level = "A"
            print(p)
            if not options.get("dry_run", None):
                p.save()

        print("--------- STARTERS A > V ---------")
        for p in models.Player.objects.filter(
            level="A", position="P", stats__career__gs__gte=126
        ):
            p.level = "V"
            print(p)
            if not options.get("dry_run", None):
                p.save()

        print("--------- RELIEVERS A > V ---------")
        for p in models.Player.objects.filter(
            level="A", position="P", stats__career__g__gte=201
        ):
            p.level = "V"
            print(p)
            if not options.get("dry_run", None):
                p.save()

        print("--------- SWINGMEN A > V ---------")
        for p in models.Player.objects.filter(
            level="A", position="P", stats__career__g__gte=220, stats__career__gs__gte=30
        ):
            p.level = "V"
            print(p)
            if not options.get("dry_run", None):
                p.save()

        print("--------- HITTERS A > V ---------")
        for p in models.Player.objects.filter(level="A", stats__career__pa__gte=2500):
            p.level = "V"
            print(p)
            if not options.get("dry_run", None):
                p.save()



    def handle(self, *args, **options):
        self.set_carded()
        self.load_career_hit()
        self.load_career_pitch()
        self.set_levels()
        self.reset_rosters()

