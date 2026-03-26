from django.core.management.base import BaseCommand
from statsdb import models


class Command(BaseCommand):
    help = 'Print player details by name'

    def add_arguments(self, parser):
        parser.add_argument('name', nargs='+', type=str)

    def handle(self, *args, **options):
        query = ' '.join(options['name'])
        players = models.Player.objects.filter(name__icontains=query).select_related('team_assigned')

        if not players:
            self.stdout.write(f'No players found matching "{query}"')
            return

        for p in players:
            self.stdout.write(f'\n--- {p.name} ---')
            self.stdout.write(f'  fg_id:        {p.fg_id}')
            self.stdout.write(f'  mlbam_id:     {p.mlbam_id}')
            self.stdout.write(f'  positions:    {p.positions}')
            self.stdout.write(f'  mlb_org:      {p.mlb_org}')
            self.stdout.write(f'  level:        {p.level}')
            self.stdout.write(f'  role:         {p.role}')
            self.stdout.write(f'  is_injured:   {p.is_injured}')
            self.stdout.write(f'  is_bench:     {p.is_bench}')
            self.stdout.write(f'  is_starter:   {p.is_starter}')
            self.stdout.write(f'  team_assigned:{p.team_assigned}')
            self.stdout.write(f'  injury_notes: {p.injury_description}')
