import sys
from http import HTTPStatus
from typing import List, Optional, ClassVar
from django.core.exceptions import (
    FieldError,
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError,
)
from django.db.models import Q, F, Avg, StdDev, Sum
from django.db.models.fields import Field
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Player, Team, Lineup, BattingStatLine, PitchingStatLine, SeasonBattingStatLine, SeasonPitchingStatLine, TeamBattingStatLine, TeamPitchingStatLine, RosterSnapshot, Draft, DraftPick
from ninja import NinjaAPI, Schema, ModelSchema, FilterSchema, Query
from ninja_extra import (api_controller, NinjaExtraAPI)
from ninja.errors import ValidationError as NinjaValidationError
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
        lineup_LF: PlayerSchema | None = None
        lineup_CF: PlayerSchema | None = None
        lineup_RF: PlayerSchema | None = None
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
        lineup_LF: str | None = None
        lineup_CF: str | None = None
        lineup_RF: str | None = None
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

class PaginatedSeasonPitchingStatLineSchema(Schema):
    results: List[SeasonPitchingStatLineSchema]
    count: int
    avg_total: float | None = None
    stddev_total: float | None = None
    sum_total: float | None = None

POSITION_SLOTS = {
    'C': ['lineup_C'],
    '1B': ['lineup_1B'],
    '2B': ['lineup_2B'],
    'SS': ['lineup_SS'],
    '3B': ['lineup_3B'],
    'LF': ['lineup_LF'],
    'CF': ['lineup_CF'],
    'RF': ['lineup_RF'],
    'OF': ['lineup_LF', 'lineup_CF', 'lineup_RF'],
    'IF': ['lineup_2B', 'lineup_SS', 'lineup_3B'],
    'IN': ['lineup_2B', 'lineup_SS', 'lineup_3B'],
    'SP': ['lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5'],
    'RP': ['lineup_RP1', 'lineup_RP2', 'lineup_RP3'],
}


class LineupAssignSchema(Schema):
    slot: str
    player_id: str

class StandingsEntrySchema(Schema):
    team: str
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


class DraftStartIn(Schema):
    order: List[str] | None = None
    rounds: int = 16


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
            'fan_total': fan_total,
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
    def player_seasons_hit(request, year:str, page: int = 1, page_size: int = 50, filters: PlayerFilterSchema = Query(PlayerFilterSchema())):
        queryset = SeasonBattingStatLine.objects.all(
            ).filter(
                year=year
            ).prefetch_related(
                'player',
            ).annotate(player_name=F('player__name')).annotate(positions=F('player__positions')).annotate(fg_id=F('player__fg_id')).annotate(team_assigned=F('player__team_assigned__abbreviation'))
        queryset = filters.filter(queryset)
        agg = queryset.filter(FAN_total__gte=0.5).aggregate(avg_total=Avg('FAN_total'), stddev_total=StdDev('FAN_total'), sum_total=Sum('FAN_total'))

        paginator = Paginator(queryset, per_page=page_size)
        if page < 1 or page > paginator.num_pages:
            return api.create_response(status=404, content={"detail": "Page does not exist."})

        paginated_data = paginator.page(page)

        return {
            "results": paginated_data,
            "count": paginator.count,
            "avg_total": agg['avg_total'],
            "stddev_total": agg['stddev_total'],
            "sum_total": float(agg['sum_total']) if agg['sum_total'] is not None else None,
        }
    @api.get("/players/{year}/pitch", response=PaginatedSeasonPitchingStatLineSchema)
    def player_seasons_pitch(request, year:str, page: int = 1, page_size: int = 50, filters: PlayerFilterSchema = Query(PlayerFilterSchema())):
        queryset = SeasonPitchingStatLine.objects.all(
            ).filter(
                year=year
            ).prefetch_related(
                'player',
            ).annotate(player_name=F('player__name')).annotate(positions=F('player__positions')).annotate(fg_id=F('player__fg_id')).annotate(team_assigned=F('player__team_assigned__abbreviation'))
        queryset = filters.filter(queryset)
        agg = queryset.filter(FAN_total__gte=0.5).aggregate(avg_total=Avg('FAN_total'), stddev_total=StdDev('FAN_total'), sum_total=Sum('FAN_total'))

        paginator = Paginator(queryset, per_page=page_size)
        if page < 1 or page > paginator.num_pages:
            return api.create_response(status=404, content={"detail": "Page does not exist."})

        paginated_data = paginator.page(page)

        return {
            "results": paginated_data,
            "count": paginator.count,
            "avg_total": agg['avg_total'],
            "stddev_total": agg['stddev_total'],
            "sum_total": float(agg['sum_total']) if agg['sum_total'] is not None else None,
        }




    @api.get("statlines/batting", response=List[BattingStatlineSchema])
    def statlines_batting(request, playerid: str):
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)
        batting_lines = BattingStatLine.objects.all().filter(player=player)
        return batting_lines

    @api.get("statlines/pitching",response=List[PitchingStatlineSchema])
    def statlines_pitching(request, playerid: str):
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)
        pitching_lines = PitchingStatLine.objects.all().filter(player=player)
        return pitching_lines

    @api.get("/season")
    def current_season(request):
        return {"season": utils.get_current_season()}

    @api.get("/standings/{year}", response=List[StandingsEntrySchema])
    def standings(request, year: str):
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
        result = []
        for abbr in set(bat) | set(pitch):
            b = bat.get(abbr, 0.0)
            p = pitch.get(abbr, 0.0)
            result.append({'team': abbr, 'bat_total': b, 'pitch_total': p, 'total': b + p})
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
            lineup_fields = [
                'lineup_C', 'lineup_1B', 'lineup_2B', 'lineup_SS', 'lineup_3B',
                'lineup_LF', 'lineup_CF', 'lineup_RF',
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
        if not open_slot:
            return api.create_response(request, {"detail": "No open lineup slot for this player"}, status=409)
        setattr(lineup, open_slot, player)
        lineup.save()
        player.team_assigned = team
        player.is_owned = True
        player.save()
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

    @api.get("/draft", response=DraftStateSchema)
    def get_draft(request):
        season = utils.get_current_season()
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

    @api.post("/draft/pick")
    def make_draft_pick(request, payload: DraftPickIn):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        try:
            team = request.user.team
        except Exception:
            return api.create_response(request, {"detail": "No team assigned to your account"}, status=400)
        season = utils.get_current_season()
        draft = get_object_or_404(Draft, year=season)
        if draft.status != 'active':
            return api.create_response(request, {"detail": "Draft is not active"}, status=400)
        current_abbr = draft.current_team_abbr()
        if team.abbreviation != current_abbr:
            return api.create_response(request, {"detail": "It is not your turn to pick"}, status=403)
        player = get_object_or_404(Player, fg_id=payload.player_fg_id)
        if player.team_assigned is not None:
            return api.create_response(request, {"detail": "Player is already owned"}, status=409)
        DraftPick.objects.create(
            draft=draft,
            pick_number=draft.current_pick,
            team=team,
            player=player,
        )
        player.team_assigned = team
        player.is_owned = True
        player.save()
        draft.current_pick += 1
        n = len(draft.order)
        if draft.current_pick > draft.rounds * n:
            draft.status = 'complete'
        draft.save()
        return {"success": True, "pick_number": draft.current_pick - 1}

    @api.post("/draft/start")
    def start_draft(request, payload: DraftStartIn):
        if not request.user.is_authenticated:
            return api.create_response(request, {"detail": "Not authenticated"}, status=401)
        if not request.user.is_staff:
            return api.create_response(request, {"detail": "Admin only"}, status=403)
        season = utils.get_current_season()
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
