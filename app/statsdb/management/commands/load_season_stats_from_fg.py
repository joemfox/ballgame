import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from statsdb import models, utils


# Python equivalents of the custom PostgreSQL scoring functions.
# These mirror the SQL in migrations/0001_initial.py.

def _fan_outs(n):
    if n is None:
        return 0.0
    n = float(n)
    v = settings.POINT_VALUES_HIT
    bp1, max1, min1 = v['outs_bp_1'], v['outs_max_1'], v['outs_min_1']
    if n <= bp1:
        return max1 * n
    return max1 * bp1 + (n - bp1) * min1


def _fan_hits(n):
    if n is None:
        return 0.0
    n = float(n)
    v = settings.POINT_VALUES_HIT
    bp1, bp2 = v['hits_bp_1'], v['hits_bp_2']
    max1, max2, min2 = v['hits_max_1'], v['hits_max_2'], v['hits_min_2']
    if n <= bp1:
        return max1 * n
    if n <= bp2:
        return (bp1 * max1) + (n - bp1) * max2
    return (bp1 * max1) + (bp2 - bp1) * max2 + (n - bp2) * min2


def _fan_hr_hit(n):
    if n is None:
        return 0.0
    n = float(n)
    v = settings.POINT_VALUES_HIT
    bp1, bp2, bp3, bp4 = v['hr_bp_1'], v['hr_bp_2'], v['hr_bp_3'], v['hr_bp_4']
    max1, max2, max3, max4, min4 = v['hr_max_1'], v['hr_max_2'], v['hr_max_3'], v['hr_max_4'], v['hr_min_4']
    if n <= bp1:
        return max1 * n
    if n <= bp2:
        return (bp1 * max1) + (n - bp1) * max2
    if n <= bp3:
        return (bp1 * max1) + (bp2 - bp1) * max2 + (n - bp2) * max3
    if n <= bp4:
        return (bp1 * max1) + (bp2 - bp1) * max2 + (bp3 - bp2) * max3 + (n - bp3) * max4
    # matches SQL ELSE (which repeats (bp2-bp1)*max2)
    return (
        (bp1 * max1)
        + (bp2 - bp1) * max2
        + (bp2 - bp1) * max2
        + (bp3 - bp2) * max3
        + (bp4 - bp3) * max4
        + (n - bp4) * min4
    )


def _fan_k_hit(n):
    if n is None:
        return 0.0
    n = float(n)
    v = settings.POINT_VALUES_HIT
    bp1, bp2 = v['k_bp_1'], v['k_bp_2']
    max1, max2, min2 = v['k_max_1'], v['k_max_2'], v['k_min_2']
    if n <= bp1:
        return max1 * n
    if n <= bp2:
        return (bp1 * max1) + (n - bp1) * max2
    return (bp1 * max1) + (bp2 - bp1) * max2 + (n - bp2) * min2


def _fan_k_pitch(n):
    if n is None:
        return 0.0
    n = float(n)
    v = settings.POINT_VALUES_PITCH
    bp1, bp2 = v['k_bp_1'], v['k_bp_2']
    max1, max2, min2 = v['k_max_1'], v['k_max_2'], v['k_min_2']
    if n <= bp1:
        return max1 * n
    if n <= bp2:
        return (bp1 * max1) + (n - bp1) * max2
    return (bp1 * max1) + (bp2 - bp1) * max2 + (n - bp2) * min2


def _fan_hr_pitch(n):
    if n is None:
        return 0.0
    n = float(n)
    v = settings.POINT_VALUES_PITCH
    bp1, bp2 = v['hr_bp_1'], v['hr_bp_2']
    max1, max2, min2 = v['hr_max_1'], v['hr_max_2'], v['hr_min_2']
    if n <= bp1:
        return max1 * n
    if n <= bp2:
        return (bp1 * max1) + (n - bp1) * max2
    return (bp1 * max1) + (bp2 - bp1) * max2 + (n - bp2) * min2


def _fan_ip(ip):
    """IP in FangGraphs notation: 2.1 = 2 full innings + 1 out."""
    if ip is None or ip == 0:
        return 0.0
    ip = float(ip)
    rate = settings.POINT_VALUES_PITCH['ip']
    if ip > 0.9:
        full = int(ip)
        frac = round(ip - full, 1)
        total_outs = (full * 3) + (frac * 10)
    else:
        total_outs = ip * 10
    return total_outs * (rate / 3)


def _fan_bool(val, point_value):
    """Boolean scoring (cycle, perfect_game, no_hitter, bs, relief_loss)."""
    if val:
        return float(point_value)
    return 0.0


def _to_int(val):
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _to_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


class Command(BaseCommand):
    help = "Load FG season stats JSON files into SeasonBattingStatLine / SeasonPitchingStatLine"

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=None,
            help='Season year to load (defaults to get_current_season())',
        )

    def handle(self, *args, **options):
        year = options['year'] or utils.get_current_season()
        self.stdout.write(f"Loading FG season stats for {year} ...")

        bat_path = f'data/{year}/fg_mlb_bat.json'
        pit_path = f'data/{year}/fg_mlb_pit.json'

        if os.path.exists(bat_path):
            self._load_batting(bat_path, year)
        else:
            self.stdout.write(self.style.WARNING(f"Batting file not found: {bat_path}"))

        if os.path.exists(pit_path):
            self._load_pitching(pit_path, year)
        else:
            self.stdout.write(self.style.WARNING(f"Pitching file not found: {pit_path}"))

        self.stdout.write(self.style.SUCCESS(f"Done loading {year} FG stats."))

    def _load_batting(self, path, year):
        with open(path, 'r') as f:
            rows = json.load(f)

        v = settings.POINT_VALUES_HIT
        loaded = skipped = 0

        for row in rows:
            fg_id = row.get('playerid')
            if not fg_id:
                skipped += 1
                continue

            player_qs = models.Player.objects.filter(fg_id=fg_id)
            if not player_qs.exists():
                skipped += 1
                continue

            player = player_qs[0]

            ab = _to_int(row.get('AB'))
            h = _to_int(row.get('H'))
            outs = (ab - h) if (ab is not None and h is not None) else None

            raw = {
                'games': _to_int(row.get('G')),
                'ab': ab,
                'r': _to_int(row.get('R')),
                'h': h,
                'outs': outs,
                'doubles': _to_int(row.get('2B')),
                'triples': _to_int(row.get('3B')),
                'hr': _to_int(row.get('HR')),
                'rbi': _to_int(row.get('RBI')),
                'bb': _to_int(row.get('BB')),
                'k': _to_int(row.get('SO')),
                'sb': _to_int(row.get('SB')),
                'cs': _to_int(row.get('CS')),
                'gidp': _to_int(row.get('GDP')),
                # not available from FG season totals
                'lob': None,
                'e': None,
                'k_looking': None,
                'rl2o': None,
                'cycle': 0,
                'po': None,
                'outfield_assists': None,
            }

            # FAN scores
            fan = {
                'FAN_outs': _fan_outs(raw['outs']),
                'FAN_h': _fan_hits(raw['h']),
                'FAN_hr': _fan_hr_hit(raw['hr']),
                'FAN_k': _fan_k_hit(raw['k']),
                'FAN_bb': (raw['bb'] or 0) * v['BB'],
                'FAN_triples': (raw['triples'] or 0) * v['triples'],
                'FAN_doubles': (raw['doubles'] or 0) * v['doubles'],
                'FAN_r': (raw['r'] or 0) * v['r'],
                'FAN_rbi': (raw['rbi'] or 0) * v['rbi'],
                'FAN_sb': (raw['sb'] or 0) * v['sb'],
                'FAN_cs': (raw['cs'] or 0) * v['cs'],
                'FAN_gidp': (raw['gidp'] or 0) * v['gidp'],
                'FAN_cycle': 0.0,
                'FAN_lob': 0.0,
                'FAN_e': 0.0,
                'FAN_k_looking': 0.0,
                'FAN_rl2o': 0.0,
                'FAN_po': 0.0,
                'FAN_outfield_assists': 0.0,
            }
            fan['FAN_total'] = sum(fan.values())

            mlbam_id = str(row.get('xMLBAMID', '')) or (player.mlbam_id or fg_id)

            stat, _ = models.SeasonBattingStatLine.objects.get_or_create(
                player=player, year=year
            )
            stat.player_mlbam_id = mlbam_id
            for k, val in raw.items():
                setattr(stat, k, val)
            for k, val in fan.items():
                setattr(stat, k, val)
            stat.save()
            loaded += 1

        self.stdout.write(f"  Batting: {loaded} loaded, {skipped} skipped")

    def _load_pitching(self, path, year):
        with open(path, 'r') as f:
            rows = json.load(f)

        v = settings.POINT_VALUES_PITCH
        loaded = skipped = 0

        for row in rows:
            fg_id = row.get('playerid')
            if not fg_id:
                skipped += 1
                continue

            player_qs = models.Player.objects.filter(fg_id=fg_id)
            if not player_qs.exists():
                skipped += 1
                continue

            player = player_qs[0]

            ip = _to_float(row.get('IP'))
            bs_count = _to_int(row.get('BS')) or 0

            raw = {
                'games': _to_int(row.get('G')),
                'ip': ip,
                'h': _to_int(row.get('H')),
                'r': _to_int(row.get('R')),
                'er': _to_int(row.get('ER')),
                'bb': _to_int(row.get('BB')),
                'k': _to_int(row.get('SO')),
                'hr': _to_int(row.get('HR')),
                'bf': _to_int(row.get('TBF')),
                'balks': _to_int(row.get('BK')),
                'hb': _to_int(row.get('HBP')),
                'wp': _to_int(row.get('WP')),
                'bs': float(bs_count),
                # not available from FG season totals
                'bra': None,
                'dpi': None,
                'e': None,
                'ir': None,
                'irs': None,
                'perfect_game': 0.0,
                'no_hitter': 0.0,
                'relief_loss': 0.0,
            }

            fan = {
                'FAN_ip': _fan_ip(ip),
                'FAN_h': (raw['h'] or 0) * v['h'],
                'FAN_er': (raw['er'] or 0) * v['er'],
                'FAN_bb': (raw['bb'] or 0) * v['bb'],
                'FAN_k': _fan_k_pitch(raw['k']),
                'FAN_hr': _fan_hr_pitch(raw['hr']),
                'FAN_bs': bs_count * v['bs'],
                'FAN_balks': (raw['balks'] or 0) * v['balks'],
                'FAN_hb': (raw['hb'] or 0) * v['hb'],
                'FAN_wp': (raw['wp'] or 0) * v['wp'],
                'FAN_bra': 0.0,
                'FAN_dpi': 0.0,
                'FAN_e': 0.0,
                'FAN_ir': 0.0,
                'FAN_irs': 0.0,
                'FAN_perfect_game': 0.0,
                'FAN_no_hitter': 0.0,
                'FAN_relief_loss': 0.0,
            }
            fan['FAN_total'] = sum(fan.values())

            mlbam_id = str(row.get('xMLBAMID', '')) or (player.mlbam_id or fg_id)

            stat, _ = models.SeasonPitchingStatLine.objects.get_or_create(
                player=player, year=year
            )
            stat.player_mlbam_id = mlbam_id
            for k, val in raw.items():
                setattr(stat, k, val)
            for k, val in fan.items():
                setattr(stat, k, val)
            stat.save()
            loaded += 1

        self.stdout.write(f"  Pitching: {loaded} loaded, {skipped} skipped")
