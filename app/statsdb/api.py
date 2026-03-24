import sys
from http import HTTPStatus
from typing import List, Optional, ClassVar
from django.core.exceptions import (
    FieldError,
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError,
)
from django.db.models import Q, F, Avg, StdDev, Sum, FloatField, Subquery, OuterRef
from django.db.models.fields import Field
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Player, Team, Lineup, BattingStatLine, PitchingStatLine, SeasonBattingStatLine, SeasonPitchingStatLine, TeamBattingStatLine, TeamPitchingStatLine, RosterSnapshot, Draft, DraftPick, Transaction, DailySchedule
from ninja import NinjaAPI, Schema, ModelSchema, FilterSchema, Query
from ninja_extra import (api_controller, NinjaExtraAPI)
from ninja.errors import ValidationError as NinjaValidationError
from django.conf import settings
from .settings import FAN_CATEGORIES_HIT
from . import utils



api = NinjaExtraAPI()

class TeamSchema(Schema):
    # city:str
    abbreviation:str = None
    # nickname:str

class TeamDetailSchema(Schema):
    city: str
    abbreviation: str
    nickname: str

class TeamUpdateSchema(Schema):
    city: str | None = None
    abbreviation: str | None = None
    nickname: str | None = None


class PlayerSchema(Schema):
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    positions:List[str] | None = None
    team_assigned: TeamSchema | None = None
    raw_age:int | None = None
    mlbam_id:str | None = None
    fg_id:str | None = None
    fan_total: float | None = None
    mlevel: str | None = None
    role: str | None = None

    
class PaginatedPlayerSchema(Schema):
    results: List[PlayerSchema]
    count: int

class PlayerFilterSchema(FilterSchema):
    search: Optional[str] = ""
    positions: Optional[List[str]] = None
    year: Optional[str] = '2026'
    ordering: Optional[str] = ""
    team: Optional[str] = None
    available: Optional[bool] = None

    def filter(self, queryset):
        combined = Q()
        if self.search:
            combined |= Q(player_name__icontains=self.search)

        if self.positions:
            position_matches = [Q(positions__icontains=position) for position in self.positions]
            combined = Q(combined, Q(*position_matches, _connector=Q.OR), _connector=Q.AND)

        if self.search or self.positions:
            queryset = queryset.filter(combined)

        if self.available is True:
            queryset = queryset.filter(player__team_assigned__isnull=True)
        elif self.available is False:
            queryset = queryset.filter(player__team_assigned__isnull=False)

        if self.team:
            queryset = queryset.filter(player__team_assigned__abbreviation=self.team)

        if self.ordering:
            queryset = queryset.order_by(self.ordering).exclude(**{f'{self.ordering.replace("-","")}__isnull':True})

        return queryset
    
class LineupSchema(Schema):
        class Config:
            arbitrary_types_allowed = True
        lineup_C: PlayerSchema | None = None
        lineup_1B: PlayerSchema | None = None
        lineup_2B: PlayerSchema | None = None
        lineup_SS: PlayerSchema | None = None
        lineup_3B: PlayerSchema | None = None
        lineup_OF1: PlayerSchema | None = None
        lineup_OF2: PlayerSchema | None = None
        lineup_OF3: PlayerSchema | None = None
        lineup_OF4: PlayerSchema | None = None
        lineup_OF5: PlayerSchema | None = None
        lineup_DH: PlayerSchema | None = None
        lineup_UTIL: PlayerSchema | None = None
        lineup_SP1: PlayerSchema | None = None
        lineup_SP2: PlayerSchema | None = None
        lineup_SP3: PlayerSchema | None = None
        lineup_SP4: PlayerSchema | None = None
        lineup_SP5: PlayerSchema | None = None
        lineup_RP1: PlayerSchema | None = None
        lineup_RP2: PlayerSchema | None = None
        lineup_RP3: PlayerSchema | None = None

class RosterActionSchema(Schema):
    player_id: str  # fg_id

class LineupIn(Schema):
        team:str
        lineup_C: str | None = None
        lineup_1B: str | None = None
        lineup_2B: str | None = None
        lineup_SS: str | None = None
        lineup_3B: str | None = None
        lineup_OF1: str | None = None
        lineup_OF2: str | None = None
        lineup_OF3: str | None = None
        lineup_OF4: str | None = None
        lineup_OF5: str | None = None
        lineup_DH: str | None = None
        lineup_UTIL: str | None = None
        lineup_SP1: str | None = None
        lineup_SP2: str | None = None
        lineup_SP3: str | None = None
        lineup_SP4: str | None = None
        lineup_SP5: str | None = None
        lineup_RP1: str | None = None
        lineup_RP2: str | None = None
        lineup_RP3: str | None = None

class BattingStatlineSchema(ModelSchema):
    class Meta:
        model = BattingStatLine
        fields = '__all__'

import datetime as _dt

class StatlinePerformanceSchema(Schema):
    date: str
    player_name: str | None = None
    fg_id: str | None = None
    type: str  # 'H' or 'P'
    FAN_total: float | None = None
    h: int | None = None
    hr: int | None = None
    r: int | None = None
    rbi: int | None = None
    sb: int | None = None
    k: int | None = None
    ip: float | None = None
    er: int | None = None

class PaginatedStatlinePerformanceSchema(Schema):
    results: List[StatlinePerformanceSchema]
    count: int

class SeasonBattingStatLineSchema(Schema):
    outs: int | None = None
    bb: int | None = None
    triples: int | None = None
    h: int | None = None
    cycle: int | None = None
    doubles: int | None = None
    outfield_assists: int | None = None
    cs: int | None = None
    e: int | None = None
    gidp: int | None = None
    hr: int | None = None
    r: int | None = None
    lob: int | None = None
    po: int | None = None
    rl2o: int | None = None
    rbi: int | None = None
    k_looking: int | None = None
    k: int | None = None
    sb: int | None = None
    FAN_outs: float | None = None
    FAN_bb: float | None = None
    FAN_triples: float | None = None
    FAN_h: float | None = None
    FAN_cycle: float | None = None
    FAN_doubles: float | None = None
    FAN_outfield_assists: float | None = None
    FAN_cs: float | None = None
    FAN_e: float | None = None
    FAN_gidp: float | None = None
    FAN_hr: float | None = None
    FAN_r: float | None = None
    FAN_lob: float | None = None
    FAN_po: float | None = None
    FAN_rl2o: float | None = None
    FAN_rbi: float | None = None
    FAN_k_looking: float | None = None
    FAN_k: float | None = None
    FAN_sb: float | None = None
    FAN_total: float | None = None
    player_name: str | None = None
    fg_id: str | None = None
    positions: List[str] | None = None
    year: int | None = None
    team_assigned: str | None = None  # team abbreviation or None if unowned
    mlb_org: str | None = None
    mlevel: str | None = None
    role: str | None = None
    is_injured: bool | None = None


class PaginatedSeasonBattingStatLineSchema(Schema):
    results: List[SeasonBattingStatLineSchema]
    count: int
    avg_total: float | None = None
    stddev_total: float | None = None
    sum_total: float | None = None

class PitchingStatlineSchema(ModelSchema):
    class Meta:
        model = PitchingStatLine
        fields = '__all__'

class SeasonPitchingStatLineSchema(Schema):
    ip: float | None = None
    h: int | None = None
    er: int | None = None
    bb: int | None = None
    k: int | None = None
    hr: int | None = None
    bs: int | None = None
    balks: int | None = None
    hb: int | None = None
    bra: int | None = None
    dpi: int | None = None
    e: int | None = None
    wp: int | None = None
    ir: int | None = None
    irs: int | None = None
    perfect_game: int | None = None
    no_hitter: int | None = None
    relief_loss: int | None = None
    FAN_ip: float | None = None
    FAN_h: float | None = None
    FAN_er: float | None = None
    FAN_bb: float | None = None
    FAN_k: float | None = None
    FAN_hr: float | None = None
    FAN_bs: float | None = None
    FAN_balks: float | None = None
    FAN_hb: float | None = None
    FAN_bra: float | None = None
    FAN_dpi: float | None = None
    FAN_e: float | None = None
    FAN_wp: float | None = None
    FAN_ir: float | None = None
    FAN_irs: float | None = None
    FAN_perfect_game: float | None = None
    FAN_no_hitter: float | None = None
    FAN_relief_loss: float | None = None
    FAN_total: float | None = None
    player_name: str | None = None
    fg_id: str | None = None
    positions: List[str] | None = None
    year: int | None = None
    team_assigned: str | None = None  # team abbreviation or None if unowned
    mlb_org: str | None = None
    mlevel: str | None = None
    role: str | None = None
    is_injured: bool | None = None

class PaginatedSeasonPitchingStatLineSchema(Schema):
    results: List[SeasonPitchingStatLineSchema]
    count: int
    avg_total: float | None = None
    stddev_total: float | None = None
    sum_total: float | None = None

class TransactionSchema(Schema):
    id: int
    player_name: str
    player_fg_id: str | None = None
    team: str
    transaction_type: str
    timestamp: str

OF_SLOTS = ['lineup_OF1', 'lineup_OF2', 'lineup_OF3', 'lineup_OF4', 'lineup_OF5']
HITTER_SLOTS = ['lineup_C', 'lineup_1B', 'lineup_2B', 'lineup_SS', 'lineup_3B'] + OF_SLOTS + ['lineup_DH', 'lineup_UTIL']

POSITION_SLOTS = {
    'C': ['lineup_C'],
    '1B': ['lineup_1B'],
    '2B': ['lineup_2B'],
    'SS': ['lineup_SS'],
    '3B': ['lineup_3B'],
    'LF': OF_SLOTS,
    'CF': OF_SLOTS,
    'RF': OF_SLOTS,
    'OF': OF_SLOTS,
    'IF': ['lineup_2B', 'lineup_SS', 'lineup_3B'],
    'IN': ['lineup_2B', 'lineup_SS', 'lineup_3B'],
    'DH': ['lineup_DH'],
    'SP': ['lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5'],
    'RP': ['lineup_RP1', 'lineup_RP2', 'lineup_RP3'],
}

# Hitter positions that can also fill the DH slot
HITTER_POSITIONS = {'C', 'IF', 'OF', 'IF-OF', 'IN', '1B', '2B', 'SS', '3B', 'LF', 'CF', 'RF', 'DH'}


class LineupAssignSchema(Schema):
    slot: str
    player_id: str

class StandingsEntrySchema(Schema):
    team: str
    team_name: str | None = None
    bat_total: float
    pitch_total: float
    total: float


class DraftPickSchema(Schema):
    pick_number: int
    team: str
    player_name: str | None = None
    player_fg_id: str | None = None
    positions: List[str] | None = None


class DraftStateSchema(Schema):
    year: int
    status: str
    current_pick: int
    current_team: str | None = None
    order: List[str]
    rounds: int
    picks: List[DraftPickSchema]


class DraftPickIn(Schema):
    player_fg_id: str


class AdminDraftPickIn(Schema):
    player_fg_id: str
    team_abbr: str


class DraftStartIn(Schema):
    order: List[str] | None = None
    rounds: int = 16


def _lineup_for_date(team_obj, date):
    lineup = get_object_or_404(Lineup, lineup_team=team_obj)

    BAT_FIELDS = [
        'ab', 'r', 'h', 'outs', 'doubles', 'triples', 'hr', 'rbi', 'bb', 'k',
        'lob', 'sb', 'cs', 'e', 'k_looking', 'rl2o', 'cycle', 'gidp', 'po', 'outfield_assists',
        'FAN_total', 'FAN_r', 'FAN_h', 'FAN_doubles', 'FAN_triples', 'FAN_hr',
        'FAN_rbi', 'FAN_sb', 'FAN_cs', 'FAN_bb', 'FAN_k', 'FAN_k_looking',
        'FAN_lob', 'FAN_gidp', 'FAN_e', 'FAN_outs', 'FAN_po', 'FAN_rl2o',
        'FAN_outfield_assists', 'FAN_cycle',
    ]
    PIT_FIELDS = [
        'ip', 'h', 'er', 'bb', 'k', 'hr', 'bs', 'hb', 'wp', 'balks', 'ir', 'irs',
        'e', 'dpi', 'bra', 'perfect_game', 'no_hitter', 'relief_loss',
        'FAN_total', 'FAN_ip', 'FAN_h', 'FAN_er', 'FAN_bb', 'FAN_k', 'FAN_hr',
        'FAN_bs', 'FAN_hb', 'FAN_wp', 'FAN_balks', 'FAN_ir', 'FAN_irs', 'FAN_e',
        'FAN_dpi', 'FAN_bra', 'FAN_perfect_game', 'FAN_no_hitter', 'FAN_relief_loss',
    ]

    def serialize(stat, fields):
        result = {}
        for f in fields:
            v = getattr(stat, f, None)
            result[f] = float(v) if hasattr(v, '__float__') and v is not None else v
        return result

    def build_rows(slots, model, fields):
        rows = []
        for slot in slots:
            player = getattr(lineup, slot)
            if not player:
                continue
            base = {
                'player_name': player.name,
                'fg_id': player.fg_id,
                'slot': slot.replace('lineup_', ''),
                'positions': list(player.positions) if player.positions else [],
                'team_assigned': team_obj.abbreviation,
                'mlevel': player.mlevel,
                'role': player.role,
                'is_injured': player.is_injured,
            }
            all_stats = list(model.objects.filter(player=player, date=date))
            if all_stats:
                for stat in all_stats:
                    row = dict(base)
                    row['game_type'] = stat.game_type
                    row.update(serialize(stat, fields))
                    rows.append(row)
            else:
                rows.append({**base, 'game_type': None})
        return rows

    hitters = build_rows([
        'lineup_C', 'lineup_1B', 'lineup_2B', 'lineup_SS', 'lineup_3B',
        'lineup_OF1', 'lineup_OF2', 'lineup_OF3', 'lineup_OF4', 'lineup_OF5',
        'lineup_DH', 'lineup_UTIL',
    ], BattingStatLine, BAT_FIELDS)

    pitchers = build_rows([
        'lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5',
        'lineup_RP1', 'lineup_RP2', 'lineup_RP3',
    ], PitchingStatLine, PIT_FIELDS)

    return {'hitters': hitters, 'pitchers': pitchers, 'date': str(date)}


@api_controller('')
class MyAPIController:
    @api.get("/player", response=PlayerSchema)
    @api.get("/player/{playerid}", response=PlayerSchema)
    def player(request, playerid: str):
        p = get_object_or_404(Player.objects.select_related('team_assigned').all(), fg_id=playerid)
        fan_total = None
        season = utils.get_current_season()
        hit_stat = SeasonBattingStatLine.objects.filter(player=p, year=season).first()
        if hit_stat:
            fan_total = float(hit_stat.FAN_total)
        else:
            pitch_stat = SeasonPitchingStatLine.objects.filter(player=p, year=season).first()
            if pitch_stat:
                fan_total = float(pitch_stat.FAN_total)
        return {
            'name': p.name, 'first_name': p.first_name, 'last_name': p.last_name,
            'positions': p.positions,
            'team_assigned': {'abbreviation': p.team_assigned.abbreviation} if p.team_assigned else None,
            'raw_age': p.raw_age, 'mlbam_id': p.mlbam_id, 'fg_id': p.fg_id,
            'fan_total': fan_total, 'mlevel': p.mlevel, 'role': p.role,
        }
    
    @api.get("/player/{playerid}/season/{year}/hit", response=SeasonBattingStatLineSchema)
    def player_season_hit(request, playerid: str, year:str):
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)
        return get_object_or_404(SeasonBattingStatLine.objects.all(), player=player, year=year)
    @api.get("/player/{playerid}/season/{year}/pitch", response=SeasonPitchingStatLineSchema)
    def player_season_pitch(request, playerid: str, year:str):
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)
        return get_object_or_404(SeasonPitchingStatLine.objects.all(), player=player, year=year)

    @api.get("/players", response=PaginatedPlayerSchema)
    def players(request, filters: PlayerFilterSchema = Query(PlayerFilterSchema()), page: int = 1, page_size: int = 50):
        queryset = Player.objects.all().order_by('fg_id')
        paginator = Paginator(queryset, per_page=page_size)
    
        if page < 1 or page > paginator.num_pages:
            return api.create_response(status=404, content={"detail": "Page does not exist."})
        
        paginated_data = paginator.page(page)

        results = [player for player in paginated_data.object_list]
        return {
            "results": results,
            "count": paginator.count,
        }
    
    @api.get("/players/{year}/hit", response=PaginatedSeasonBattingStatLineSchema)
    def player_seasons_hit(request, year: str, page: int = 1, page_size: int = 50, filters: PlayerFilterSchema = Query(PlayerFilterSchema())):
        HIT_FIELDS = [
            'outs', 'bb', 'triples', 'h', 'cycle', 'doubles', 'outfield_assists',
            'cs', 'e', 'gidp', 'hr', 'r', 'lob', 'po', 'rl2o', 'rbi', 'k_looking', 'k', 'sb',
            'FAN_outs', 'FAN_bb', 'FAN_triples', 'FAN_h', 'FAN_cycle', 'FAN_doubles',
            'FAN_outfield_assists', 'FAN_cs', 'FAN_e', 'FAN_gidp', 'FAN_hr', 'FAN_r',
            'FAN_lob', 'FAN_po', 'FAN_rl2o', 'FAN_rbi', 'FAN_k_looking', 'FAN_k', 'FAN_sb', 'FAN_total',
        ]
        stat_sq = SeasonBattingStatLine.objects.filter(player=OuterRef('pk'), year=year)
        queryset = Player.objects.exclude(position='P').select_related('team_assigned').annotate(
            FAN_total=Subquery(stat_sq.values('FAN_total')[:1], output_field=FloatField()),
        )
        # Apply filters on Player fields
        if filters.search:
            queryset = queryset.filter(name__icontains=filters.search)
        if filters.positions:
            pos_q = Q(
                *[
                    Q(positions__contains=[p])
                    for p in filters.positions
                ],
                _connector=Q.OR,
            )
            queryset = queryset.filter(pos_q)
        if filters.available is True:
            queryset = queryset.filter(team_assigned__isnull=True)
        elif filters.team:
            queryset = queryset.filter(team_assigned__abbreviation=filters.team)
        if filters.ordering:
            sort_field = filters.ordering.lstrip('-')
            desc = filters.ordering.startswith('-')
            player_fields = {f.name for f in Player._meta.get_fields()}
            if sort_field not in player_fields and sort_field != 'FAN_total':
                extra_sq = SeasonBattingStatLine.objects.filter(player=OuterRef('pk'), year=year)
                queryset = queryset.annotate(
                    **{sort_field: Subquery(extra_sq.values(sort_field)[:1], output_field=FloatField())}
                )
            f = F(sort_field)
            queryset = queryset.order_by(f.desc(nulls_last=True) if desc else f.asc(nulls_last=True))
        else:
            queryset = queryset.order_by(F('FAN_total').desc(nulls_last=True))

        # Aggregate from SeasonBattingStatLine for stats display
        agg_filter = Q(year=year, FAN_total__gte=0.5)
        if filters.team:
            agg_filter &= Q(player__team_assigned__abbreviation=filters.team)
        agg = SeasonBattingStatLine.objects.filter(agg_filter).aggregate(
            avg_total=Avg('FAN_total'), stddev_total=StdDev('FAN_total'), sum_total=Sum('FAN_total')
        )

        paginator = Paginator(queryset, per_page=page_size)
        if page < 1 or page > paginator.num_pages:
            return api.create_response(status=404, content={"detail": "Page does not exist."})

        paginated_players = paginator.page(page)
        player_pks = [p.pk for p in paginated_players]
        stat_map = {s.player_id: s for s in SeasonBattingStatLine.objects.filter(player_id__in=player_pks, year=year)}

        results = []
        for player in paginated_players:
            stat = stat_map.get(player.pk)
            entry = {
                'player_name': player.name,
                'fg_id': player.fg_id,
                'positions': player.positions or [],
                'year': int(year),
                'team_assigned': player.team_assigned.abbreviation if player.team_assigned else None,
                'mlb_org': player.mlb_org,
                'mlevel': player.mlevel,
                'role': player.role,
                'is_injured': player.is_injured,
            }
            if stat:
                for field in HIT_FIELDS:
                    entry[field] = getattr(stat, field, None)
            results.append(entry)

        return {
            "results": results,
            "count": paginator.count,
            "avg_total": agg['avg_total'],
            "stddev_total": agg['stddev_total'],
            "sum_total": float(agg['sum_total']) if agg['sum_total'] is not None else None,
        }

    @api.get("/players/{year}/pitch", response=PaginatedSeasonPitchingStatLineSchema)
    def player_seasons_pitch(request, year: str, page: int = 1, page_size: int = 50, filters: PlayerFilterSchema = Query(PlayerFilterSchema())):
        PITCH_FIELDS = [
            'ip', 'h', 'er', 'bb', 'k', 'hr', 'bs', 'balks', 'hb', 'bra', 'dpi', 'e', 'wp',
            'ir', 'irs', 'perfect_game', 'no_hitter', 'relief_loss',
            'FAN_ip', 'FAN_h', 'FAN_er', 'FAN_bb', 'FAN_k', 'FAN_hr', 'FAN_bs', 'FAN_balks',
            'FAN_hb', 'FAN_bra', 'FAN_dpi', 'FAN_e', 'FAN_wp', 'FAN_ir', 'FAN_irs',
            'FAN_perfect_game', 'FAN_no_hitter', 'FAN_relief_loss', 'FAN_total',
        ]
        stat_sq = SeasonPitchingStatLine.objects.filter(player=OuterRef('pk'), year=year)
        queryset = Player.objects.filter(position='P').select_related('team_assigned').annotate(
            FAN_total=Subquery(stat_sq.values('FAN_total')[:1], output_field=FloatField()),
        )
        if filters.search:
            queryset = queryset.filter(name__icontains=filters.search)
        if filters.positions:
            pos_q = Q(*[Q(positions__icontains=p) for p in filters.positions], _connector=Q.OR)
            queryset = queryset.filter(pos_q)
        if filters.available is True:
            queryset = queryset.filter(team_assigned__isnull=True)
        elif filters.team:
            queryset = queryset.filter(team_assigned__abbreviation=filters.team)
        if filters.ordering:
            sort_field = filters.ordering.lstrip('-')
            desc = filters.ordering.startswith('-')
            player_fields = {f.name for f in Player._meta.get_fields()}
            if sort_field not in player_fields and sort_field != 'FAN_total':
                extra_sq = SeasonPitchingStatLine.objects.filter(player=OuterRef('pk'), year=year)
                queryset = queryset.annotate(
                    **{sort_field: Subquery(extra_sq.values(sort_field)[:1], output_field=FloatField())}
                )
            f = F(sort_field)
            queryset = queryset.order_by(f.desc(nulls_last=True) if desc else f.asc(nulls_last=True))
        else:
            queryset = queryset.order_by(F('FAN_total').desc(nulls_last=True))

        agg_filter = Q(year=year, FAN_total__gte=0.5)
        if filters.team:
            agg_filter &= Q(player__team_assigned__abbreviation=filters.team)
        agg = SeasonPitchingStatLine.objects.filter(agg_filter).aggregate(
            avg_total=Avg('FAN_total'), stddev_total=StdDev('FAN_total'), sum_total=Sum('FAN_total')
        )

        paginator = Paginator(queryset, per_page=page_size)
        if page < 1 or page > paginator.num_pages:
            return api.create_response(status=404, content={"detail": "Page does not exist."})

        paginated_players = paginator.page(page)
        player_pks = [p.pk for p in paginated_players]
        stat_map = {s.player_id: s for s in SeasonPitchingStatLine.objects.filter(player_id__in=player_pks, year=year)}

        results = []
        for player in paginated_players:
            stat = stat_map.get(player.pk)
            entry = {
                'player_name': player.name,
                'fg_id': player.fg_id,
                'positions': player.positions or [],
                'year': int(year),
                'team_assigned': player.team_assigned.abbreviation if player.team_assigned else None,
                'mlb_org': player.mlb_org,
                'mlevel': player.mlevel,
                'role': player.role,
                'is_injured': player.is_injured,
            }
            if stat:
                for field in PITCH_FIELDS:
                    entry[field] = getattr(stat, field, None)
            results.append(entry)

        return {
            "results": results,
            "count": paginator.count,
            "avg_total": agg['avg_total'],
            "stddev_total": agg['stddev_total'],
            "sum_total": float(agg['sum_total']) if agg['sum_total'] is not None else None,
        }




    @api.get("/players/{year}/hit/column-ranges")
    def hit_column_ranges(request, year: str):
        from django.db.models import Min, Max
        FIELDS = [
            'outs', 'bb', 'triples', 'h', 'cycle', 'doubles', 'outfield_assists',
            'cs', 'e', 'gidp', 'hr', 'r', 'lob', 'po', 'rl2o', 'rbi', 'k_looking', 'k', 'sb',
            'FAN_outs', 'FAN_bb', 'FAN_triples', 'FAN_h', 'FAN_cycle', 'FAN_doubles',
            'FAN_outfield_assists', 'FAN_cs', 'FAN_e', 'FAN_gidp', 'FAN_hr', 'FAN_r',
            'FAN_lob', 'FAN_po', 'FAN_rl2o', 'FAN_rbi', 'FAN_k_looking', 'FAN_k', 'FAN_sb',
        ]
        agg = SeasonBattingStatLine.objects.filter(year=year).aggregate(
            **{f'{f}__min': Min(f) for f in FIELDS},
            **{f'{f}__max': Max(f) for f in FIELDS},
        )
        return {f: {'min': agg.get(f'{f}__min'), 'max': agg.get(f'{f}__max')} for f in FIELDS}

    @api.get("/players/{year}/pitch/column-ranges")
    def pitch_column_ranges(request, year: str):
        from django.db.models import Min, Max
        FIELDS = [
            'ip', 'h', 'er', 'bb', 'k', 'hr', 'bs', 'balks', 'hb', 'bra', 'dpi', 'e', 'wp',
            'ir', 'irs', 'perfect_game', 'no_hitter', 'relief_loss',
            'FAN_ip', 'FAN_h', 'FAN_er', 'FAN_bb', 'FAN_k', 'FAN_hr', 'FAN_bs', 'FAN_balks',
            'FAN_hb', 'FAN_bra', 'FAN_dpi', 'FAN_e', 'FAN_wp', 'FAN_ir', 'FAN_irs',
            'FAN_perfect_game', 'FAN_no_hitter', 'FAN_relief_loss',
        ]
        agg = SeasonPitchingStatLine.objects.filter(year=year).aggregate(
            **{f'{f}__min': Min(f) for f in FIELDS},
            **{f'{f}__max': Max(f) for f in FIELDS},
        )
        return {f: {'min': agg.get(f'{f}__min'), 'max': agg.get(f'{f}__max')} for f in FIELDS}

    @api.get("statlines/batting", response=List[BattingStatlineSchema])
    def statlines_batting(request, playerid: str, year: str = None):
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)
        qs = BattingStatLine.objects.filter(player=player).filter(Q(game_type='R') | Q(game_type__isnull=True))
        if year:
            qs = qs.filter(date__year=year)
        return qs.order_by('date')

    @api.get("statlines/pitching", response=List[PitchingStatlineSchema])
    def statlines_pitching(request, playerid: str, year: str = None):
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)
        qs = PitchingStatLine.objects.filter(player=player).filter(Q(game_type='R') | Q(game_type__isnull=True))
        if year:
            qs = qs.filter(date__year=year)
        return qs.order_by('date')

    @api.get("statlines/today")
    def statlines_today(request, playerid: str, date: str = None):
        if date:
            try:
                today_utc = _dt.date.fromisoformat(date)
            except ValueError:
                today_utc = _dt.datetime.now(_dt.timezone.utc).date()
        else:
            today_utc = _dt.datetime.now(_dt.timezone.utc).date()
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)

        def serialize_stat(stat, fields):
            row = {'date': str(stat.date), 'game_type': stat.game_type}
            for f in fields:
                v = getattr(stat, f, None)
                row[f] = float(v) if hasattr(v, '__float__') and v is not None else v
            return row

        BAT_FIELDS = [
            'ab', 'r', 'h', 'outs', 'doubles', 'triples', 'hr', 'rbi', 'bb', 'k',
            'lob', 'sb', 'cs', 'e', 'k_looking', 'rl2o', 'cycle', 'gidp', 'po', 'outfield_assists',
            'FAN_total', 'FAN_r', 'FAN_h', 'FAN_doubles', 'FAN_triples', 'FAN_hr',
            'FAN_rbi', 'FAN_sb', 'FAN_cs', 'FAN_bb', 'FAN_k', 'FAN_k_looking',
            'FAN_lob', 'FAN_gidp', 'FAN_e', 'FAN_outs', 'FAN_po', 'FAN_rl2o',
            'FAN_outfield_assists', 'FAN_cycle',
        ]
        PIT_FIELDS = [
            'ip', 'h', 'er', 'bb', 'k', 'hr', 'bs', 'hb', 'wp', 'balks', 'ir', 'irs',
            'e', 'dpi', 'bra', 'perfect_game', 'no_hitter', 'relief_loss',
            'FAN_total', 'FAN_ip', 'FAN_h', 'FAN_er', 'FAN_bb', 'FAN_k', 'FAN_hr',
            'FAN_bs', 'FAN_hb', 'FAN_wp', 'FAN_balks', 'FAN_ir', 'FAN_irs', 'FAN_e',
            'FAN_dpi', 'FAN_bra', 'FAN_perfect_game', 'FAN_no_hitter', 'FAN_relief_loss',
        ]

        batting = [serialize_stat(s, BAT_FIELDS) for s in BattingStatLine.objects.filter(player=player, date=today_utc)]
        pitching = [serialize_stat(s, PIT_FIELDS) for s in PitchingStatLine.objects.filter(player=player, date=today_utc)]
        return {'batting': batting, 'pitching': pitching, 'date': str(today_utc)}

    @api.get("statlines/team", response=PaginatedStatlinePerformanceSchema)
    def statlines_team(request, team: str, year: str, page: int = 1):
        PAGE_SIZE = 5
        team_obj = get_object_or_404(Team, abbreviation=team)
        rs_filter = Q(game_type='R')

        bat = list(BattingStatLine.objects.filter(
            fantasy_team=team_obj, date__year=year
        ).filter(rs_filter).values('date', 'FAN_total', 'player__name', 'player__fg_id', 'h', 'hr', 'r', 'rbi', 'sb', 'k'))
        for row in bat:
            row['type'] = 'H'
            row['player_name'] = row.pop('player__name')
            row['fg_id'] = row.pop('player__fg_id')
            row['date'] = str(row['date'])
            row['ip'] = None
            row['er'] = None

        pitch = list(PitchingStatLine.objects.filter(
            fantasy_team=team_obj, date__year=year
        ).filter(rs_filter).values('date', 'FAN_total', 'player__name', 'player__fg_id', 'ip', 'k', 'er', 'hr', 'h'))
        for row in pitch:
            row['type'] = 'P'
            row['player_name'] = row.pop('player__name')
            row['fg_id'] = row.pop('player__fg_id')
            row['date'] = str(row['date'])
            row['r'] = None
            row['rbi'] = None
            row['sb'] = None
            row['ip'] = float(row['ip']) if row['ip'] is not None else None

        combined = sorted(bat + pitch, key=lambda x: x['FAN_total'] or 0, reverse=True)
        count = len(combined)
        start = (page - 1) * PAGE_SIZE
        return {'results': combined[start:start + PAGE_SIZE], 'count': count}

    @api.get("/season")
    def current_season(request):
        return {"season": utils.get_current_season(), "upcoming_season": settings.CURRENT_SEASON}

    @api.get("/schedule/lock_time")
    def roster_lock_time(request, date: str = None):
        import datetime as _dt
        if date:
            try:
                target_date = _dt.date.fromisoformat(date)
            except ValueError:
                target_date = _dt.date.today()
        else:
            target_date = _dt.date.today()

        try:
            sched = DailySchedule.objects.get(date=target_date)
            lock_time = sched.roster_lock_time
            now_utc = _dt.datetime.now(_dt.timezone.utc)
            is_locked = lock_time is not None and lock_time <= now_utc
            return {
                'date': str(target_date),
                'roster_lock_time': lock_time.isoformat() if lock_time else None,
                'is_locked': is_locked,
            }
        except DailySchedule.DoesNotExist:
            return {'date': str(target_date), 'roster_lock_time': None, 'is_locked': False}

    @api.get("/standings/sombrero/{year}")
    def sombrero_standings(request, year: str):
        results = (
            TeamBattingStatLine.objects
            .filter(date__year=year)
            .values('team__abbreviation', 'team__city', 'team__nickname')
            .annotate(total=Sum('sombrero'))
            .order_by('-total')
        )
        return [{'team': r['team__abbreviation'], 'team_name': f"{r['team__city']} {r['team__nickname']}".strip(), 'sombrero': int(r['total'] or 0)} for r in results]

    @api.get("/standings/{year}", response=List[StandingsEntrySchema])
    def standings(request, year: str):
        team_names = {t.abbreviation: f"{t.city} {t.nickname}".strip() for t in Team.objects.all()}
        bat = {
            r['team__abbreviation']: float(r['total'] or 0)
            for r in TeamBattingStatLine.objects.filter(date__year=year)
                .values('team__abbreviation')
                .annotate(total=Sum('FAN_total'))
        }
        pitch = {
            r['team__abbreviation']: float(r['total'] or 0)
            for r in TeamPitchingStatLine.objects.filter(date__year=year)
                .values('team__abbreviation')
                .annotate(total=Sum('FAN_total'))
        }
        team_abbrs = set(bat) | set(pitch) or set(team_names)
        result = []
        for abbr in team_abbrs:
            b = bat.get(abbr, 0.0)
            p = pitch.get(abbr, 0.0)
            result.append({'team': abbr, 'team_name': team_names.get(abbr), 'bat_total': b, 'pitch_total': p, 'total': b + p})
        result.sort(key=lambda x: x['total'], reverse=True)
        return result

    @api.get("/roster", response=List[PlayerSchema])
    def roster(request):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        try:
            team = request.user.team
        except Exception:
            return []
        return Player.objects.filter(team_assigned=team).order_by('name')

    @api.post("/roster/add")
    def roster_add(request, payload: RosterActionSchema):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        try:
            team = request.user.team
        except Exception:
            return api.create_response(request, {"detail": "No team assigned to your account"}, status=400)
        player = get_object_or_404(Player, fg_id=payload.player_id)
        if player.team_assigned is not None:
            return api.create_response(request, {"detail": "Player is already on a roster"}, status=409)
        player.team_assigned = team
        player.is_owned = True
        player.save()
        Transaction.objects.create(player=player, team=team, transaction_type=Transaction.ADD)
        return {"success": True}

    @api.post("/roster/drop")
    def roster_drop(request, payload: RosterActionSchema):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        try:
            team = request.user.team
        except Exception:
            return api.create_response(request, {"detail": "No team assigned to your account"}, status=400)
        player = get_object_or_404(Player, fg_id=payload.player_id)
        if player.team_assigned != team:
            return api.create_response(request, {"detail": "Player is not on your roster"}, status=403)
        # Remove from lineup if present
        try:
            lineup = Lineup.objects.get(lineup_team=team)
            lineup_fields = HITTER_SLOTS + [
                'lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5',
                'lineup_RP1', 'lineup_RP2', 'lineup_RP3',
            ]
            changed = False
            for field in lineup_fields:
                if getattr(lineup, field) == player:
                    setattr(lineup, field, None)
                    changed = True
            if changed:
                lineup.save()
        except Lineup.DoesNotExist:
            pass
        Transaction.objects.create(player=player, team=team, transaction_type=Transaction.DROP)
        player.team_assigned = None
        player.is_owned = False
        player.save()
        return {"success": True}

    @api.post("/lineup/add")
    def lineup_add(request, payload: RosterActionSchema):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        try:
            team = request.user.team
        except Exception:
            return api.create_response(request, {"detail": "No team assigned to your account"}, status=400)
        player = get_object_or_404(Player, fg_id=payload.player_id)
        if player.team_assigned is not None:
            return api.create_response(request, {"detail": "Player is already on a roster"}, status=409)
        lineup, _ = Lineup.objects.get_or_create(lineup_team=team)
        open_slot = None
        for position in (player.positions or []):
            for slot in POSITION_SLOTS.get(position, []):
                if getattr(lineup, slot) is None:
                    open_slot = slot
                    break
            if open_slot:
                break
        # Any hitter can fill UTIL as a fallback
        if not open_slot and any(p in HITTER_POSITIONS for p in (player.positions or [])):
            for slot in ['lineup_DH', 'lineup_UTIL']:
                if getattr(lineup, slot) is None:
                    open_slot = slot
                    break
        if not open_slot:
            return api.create_response(request, {"detail": "No open lineup slot for this player"}, status=409)
        setattr(lineup, open_slot, player)
        lineup.save()
        player.team_assigned = team
        player.is_owned = True
        player.save()
        Transaction.objects.create(player=player, team=team, transaction_type=Transaction.ADD)
        return {"success": True, "slot": open_slot}

    @api.post("/lineup/assign")
    def lineup_assign(request, payload: LineupAssignSchema):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        try:
            team = request.user.team
        except Exception:
            return api.create_response(request, {"detail": "No team assigned to your account"}, status=400)
        player = get_object_or_404(Player, fg_id=payload.player_id)
        if player.team_assigned is not None and player.team_assigned != team:
            return api.create_response(request, {"detail": "Player is on another team's roster"}, status=409)
        if not hasattr(Lineup(), payload.slot):
            return api.create_response(request, {"detail": "Invalid slot"}, status=400)
        if player.position == 'DH' and payload.slot != 'lineup_DH':
            return api.create_response(request, {"detail": "DH players can only be placed in the DH slot"}, status=400)
        lineup, _ = Lineup.objects.get_or_create(lineup_team=team)
        setattr(lineup, payload.slot, player)
        lineup.save()
        if player.team_assigned != team:
            player.team_assigned = team
            player.is_owned = True
            player.save()
        return {"success": True}

    @api.get("/lineup", response=LineupSchema)
    def lineup(request,team: str):
        team_obj = get_object_or_404(Team.objects.all(),abbreviation=team)
        lineup = get_object_or_404(Lineup.objects.all(),lineup_team=team_obj)
        return lineup

    @api.get("/lineup/full")
    def lineup_full(request, team: str):
        SLOTS = [
            'lineup_C', 'lineup_1B', 'lineup_2B', 'lineup_SS', 'lineup_3B',
            'lineup_OF1', 'lineup_OF2', 'lineup_OF3', 'lineup_OF4', 'lineup_OF5',
            'lineup_DH', 'lineup_UTIL',
            'lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5',
            'lineup_RP1', 'lineup_RP2', 'lineup_RP3',
        ]
        team_obj = get_object_or_404(Team, abbreviation=team)
        lineup = get_object_or_404(
            Lineup.objects.select_related(*[f'{s}__team_assigned' for s in SLOTS]),
            lineup_team=team_obj,
        )
        season = utils.get_current_season()
        players = {s: getattr(lineup, s) for s in SLOTS if getattr(lineup, s) is not None}
        player_pks = list({p.pk for p in players.values()})
        hit_totals = {s.player_id: float(s.FAN_total) for s in SeasonBattingStatLine.objects.filter(player_id__in=player_pks, year=season) if s.FAN_total is not None}
        pitch_totals = {s.player_id: float(s.FAN_total) for s in SeasonPitchingStatLine.objects.filter(player_id__in=player_pks, year=season) if s.FAN_total is not None}
        result = {}
        for slot in SLOTS:
            p = players.get(slot)
            if p is None:
                result[slot] = None
            else:
                result[slot] = {
                    'name': p.name, 'first_name': p.first_name, 'last_name': p.last_name,
                    'positions': p.positions, 'mlbam_id': p.mlbam_id, 'fg_id': p.fg_id,
                    'raw_age': p.raw_age, 'mlevel': p.mlevel, 'role': p.role, 'is_injured': p.is_injured,
                    'team_assigned': {'abbreviation': p.team_assigned.abbreviation} if p.team_assigned else None,
                    'fan_total': hit_totals.get(p.pk) or pitch_totals.get(p.pk),
                }
        return result

    @api.get("/transactions", response=List[TransactionSchema])
    def transactions(request):
        qs = Transaction.objects.select_related('player', 'team').order_by('-timestamp')[:200]
        return [
            TransactionSchema(
                id=t.id,
                player_name=t.player.name,
                player_fg_id=t.player.fg_id,
                team=t.team.abbreviation,
                transaction_type=t.transaction_type,
                timestamp=t.timestamp.isoformat(),
            )
            for t in qs
        ]

    @api.get("/lineup/yesterday")
    def lineup_yesterday(request, team: str):
        yesterday = _dt.date.today() - _dt.timedelta(days=1)
        team_obj = get_object_or_404(Team, abbreviation=team)
        return _lineup_for_date(team_obj, yesterday)

    @api.get("/lineup/today")
    def lineup_today(request, team: str, date: str = None):
        if date:
            try:
                today = _dt.date.fromisoformat(date)
            except ValueError:
                today = _dt.datetime.now(_dt.timezone.utc).date()
        else:
            today = _dt.datetime.now(_dt.timezone.utc).date()
        team_obj = get_object_or_404(Team, abbreviation=team)
        return _lineup_for_date(team_obj, today)

    @api.post('/lineup')
    def updateLineup(request, payload: LineupIn):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        team_obj = get_object_or_404(Team.objects.all(), abbreviation=payload.team)
        try:
            if request.user.team != team_obj:
                return api.create_response(request, {"detail": "Not authorized"}, status=403)
        except Exception:
            return api.create_response(request, {"detail": "No team assigned"}, status=400)
        lineup = get_object_or_404(Lineup.objects.all(), lineup_team=team_obj)
        for attr, value in payload.dict(exclude_unset=True).items():
            if attr != 'team':
                if value is None:
                    setattr(lineup, attr, None)
                else:
                    player = get_object_or_404(Player.objects.all(), fg_id=value)
                    setattr(lineup, attr, player)
                    player.team_assigned = team_obj
                    player.save()
        lineup.save()
        return {"success": True}
        

    @api.get("/team", response=TeamDetailSchema)
    def get_team(request):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        try:
            t = request.user.team
        except Exception:
            return api.create_response(request, {"detail": "No team"}, status=404)
        return {"city": t.city, "abbreviation": t.abbreviation, "nickname": t.nickname}

    @api.patch("/team", response=TeamDetailSchema)
    def update_team(request, payload: TeamUpdateSchema):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        try:
            t = request.user.team
        except Exception:
            return api.create_response(request, {"detail": "No team"}, status=404)
        if payload.city is not None:
            t.city = payload.city
        if payload.nickname is not None:
            t.nickname = payload.nickname
        if payload.abbreviation is not None:
            abbr = payload.abbreviation.upper()[:3]
            if Team.objects.exclude(pk=t.pk).filter(abbreviation=abbr).exists():
                return api.create_response(request, {"detail": "Abbreviation already in use"}, status=409)
            t.abbreviation = abbr
        t.save()
        return {"city": t.city, "abbreviation": t.abbreviation, "nickname": t.nickname}

    @api.get("/team/{abbr}", response=TeamDetailSchema)
    def get_team_by_abbr(request, abbr: str):
        t = get_object_or_404(Team, abbreviation=abbr)
        return {"city": t.city, "abbreviation": t.abbreviation, "nickname": t.nickname}

    @api.get("/draft", response=DraftStateSchema)
    def get_draft(request):
        season = utils.get_current_season()
        is_offseason = utils.get_current_season_type() == "offseason"
        season = (season + 1) if is_offseason else season
        draft = Draft.objects.filter(year=season).first()
        if draft is None:
            return api.create_response(request, {"detail": "No draft found for current season"}, status=404)
        n = len(draft.order)
        made = {p.pick_number: p for p in draft.picks.select_related('team', 'player').all()}
        picks = []
        for pick_num in range(1, draft.rounds * n + 1):
            round_num = (pick_num - 1) // n
            pos = (pick_num - 1) % n
            team_abbr = draft.order[pos] if round_num % 2 == 0 else draft.order[n - 1 - pos]
            p = made.get(pick_num)
            picks.append({
                'pick_number': pick_num,
                'team': team_abbr,
                'player_name': p.player.name if p and p.player else None,
                'player_fg_id': p.player.fg_id if p and p.player else None,
                'positions': p.player.positions if p and p.player else None,
            })
        return {
            'year': draft.year,
            'status': draft.status,
            'current_pick': draft.current_pick,
            'current_team': draft.current_team_abbr(),
            'order': draft.order,
            'rounds': draft.rounds,
            'picks': picks,
        }

    def _assign_draft_pick(self, draft, team, player):
        """Record the pick, assign to team, advance draft, auto-slot into lineup. Returns slot or None."""
        DraftPick.objects.create(draft=draft, pick_number=draft.current_pick, team=team, player=player)
        player.team_assigned = team
        player.is_owned = True
        player.save()
        draft.current_pick += 1
        if draft.current_pick > draft.rounds * len(draft.order):
            draft.status = 'complete'
        draft.save()
        open_slot = None
        lineup, _ = Lineup.objects.get_or_create(lineup_team=team)
        for position in (player.positions or []):
            for slot in POSITION_SLOTS.get(position, []):
                if getattr(lineup, slot) is None:
                    open_slot = slot
                    break
            if open_slot:
                break
        if not open_slot and any(p in HITTER_POSITIONS for p in (player.positions or [])):
            for slot in ['lineup_DH', 'lineup_UTIL']:
                if getattr(lineup, slot) is None:
                    open_slot = slot
                    break
        if open_slot:
            setattr(lineup, open_slot, player)
            lineup.save()
        return open_slot

    @api.post("/draft/pick")
    def make_draft_pick(request, payload: DraftPickIn):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        try:
            team = request.user.team
        except Exception:
            return api.create_response(request, {"detail": "No team assigned to your account"}, status=400)
        season = utils.get_current_season()
        if utils.get_current_season_type() == "offseason":
            season += 1
        draft = get_object_or_404(Draft, year=season)
        if draft.status != 'active':
            return api.create_response(request, {"detail": "Draft is not active"}, status=400)
        current_abbr = draft.current_team_abbr()
        if team.abbreviation != current_abbr:
            return api.create_response(request, {"detail": "It is not your turn to pick"}, status=403)
        player = get_object_or_404(Player, fg_id=payload.player_fg_id)
        if player.team_assigned is not None:
            return api.create_response(request, {"detail": "Player is already owned"}, status=409)
        pick_number = draft.current_pick
        slot = MyAPIController._assign_draft_pick(None, draft, team, player)
        return {"success": True, "pick_number": pick_number, "slot": slot}

    @api.post("/draft/start")
    def start_draft(request, payload: DraftStartIn):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        if not request.user.is_staff:
            return api.create_response(request, {"detail": "Admin only"}, status=403)
        season = utils.get_current_season()
        if utils.get_current_season_type() == "offseason":
            season += 1
        order = payload.order or [t.abbreviation for t in Team.objects.filter(user__isnull=False).order_by('abbreviation')]
        draft, created = Draft.objects.get_or_create(
            year=season,
            defaults={'order': order, 'rounds': payload.rounds, 'status': 'active', 'current_pick': 1},
        )
        if not created:
            draft.status = 'active'
            draft.order = order
            draft.rounds = payload.rounds
            draft.current_pick = 1
            draft.save()
        return {"success": True, "year": season, "order": draft.order}

    @api.post("/draft/admin-pick")
    def admin_draft_pick(request, payload: AdminDraftPickIn):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        if not request.user.is_staff:
            return api.create_response(request, {"detail": "Admin only"}, status=403)
        season = utils.get_current_season()
        if utils.get_current_season_type() == "offseason":
            season += 1
        draft = get_object_or_404(Draft, year=season)
        if draft.status != 'active':
            return api.create_response(request, {"detail": "Draft is not active"}, status=400)
        team = get_object_or_404(Team, abbreviation=payload.team_abbr)
        current_abbr = draft.current_team_abbr()
        if team.abbreviation != current_abbr:
            return api.create_response(request, {"detail": f"It is {current_abbr}'s turn, not {team.abbreviation}"}, status=403)
        player = get_object_or_404(Player, fg_id=payload.player_fg_id)
        if player.team_assigned is not None:
            return api.create_response(request, {"detail": "Player is already owned"}, status=409)
        pick_number = draft.current_pick
        slot = MyAPIController._assign_draft_pick(None, draft, team, player)
        return {"success": True, "pick_number": pick_number, "slot": slot}

    @api.exception_handler(ObjectDoesNotExist)
    def handle_object_does_not_exist(request, exc):
        return api.create_response(
            request,
            {"message": "ObjectDoesNotExist", "detail": str(exc)},
            status=HTTPStatus.NOT_FOUND,
        )

    @api.exception_handler(PermissionDenied)
    def handle_permission_error(request, exc: PermissionDenied):
        return api.create_response(
            request,
            {
                "message": "PermissionDenied",
                "detail": "You don't have the permission to access this resource.",
            },
            status=HTTPStatus.FORBIDDEN,
        )

    @api.exception_handler(NinjaValidationError)
    def handle_ninja_validation_error(request, exc: NinjaValidationError):
        mapped_msg = {error["loc"][-1]: error["msg"] for error in exc.errors}
        return api.create_response(
            request,
            data={"message": "NinjaValidationError", "detail": mapped_msg},
            status=HTTPStatus.BAD_REQUEST,
        )

    @api.exception_handler(ValidationError)
    def handle_validation_error(request, exc: ValidationError):
        status = HTTPStatus.BAD_REQUEST
        for field, errors in exc.error_dict.items():
            for error in errors:
                if error.code in ["unique", "unique_together"]:
                    status = HTTPStatus.CONFLICT
        return api.create_response(
            request,
            data={"message": "ValidationError", "detail": exc.message_dict},
            status=status,
        )

    @api.exception_handler(FieldError)
    def handle_field_error(request, exc: FieldError):
        return api.create_response(
            request,
            data={"message": "FieldError", "detail": str(exc)},
            status=HTTPStatus.BAD_REQUEST,
        )


api.register_controllers(MyAPIController)
