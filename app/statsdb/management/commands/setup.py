from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from statsdb import models, utils


class Command(BaseCommand):
    def handle(self, *args, **options):
        # call_command("download_fg_rosters")
        # call_command("download_mlb_depthcharts")
        # call_command("download_fg_stats")
        # call_command("load_rosters")
        call_command("scrape_mlb_data")
        call_command("import_names")
        call_command("update_status_from_fg_rosters")
        call_command("update_stats_from_fg_stats")