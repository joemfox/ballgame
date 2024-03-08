from http import HTTPStatus
from typing import List, Optional, ClassVar
from django.core.exceptions import (
    FieldError,
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError,
)
from django.db.models import Q
from django.db.models.fields import Field
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Player, Team, Lineup, BattingStatLine, PitchingStatLine, SeasonBattingStatLine
from ninja import NinjaAPI, Schema, ModelSchema, FilterSchema, Query
from ninja_extra import (api_controller, NinjaExtraAPI)
from ninja.errors import ValidationError as NinjaValidationError
from .settings import FAN_CATEGORIES_HIT


api = NinjaExtraAPI()

class TeamSchema(Schema):
    # city:str 
    abbreviation:str = None
    # nickname:str


class PlayerSchema(Schema):
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    positions:List[str] | None = None
    team_assigned: TeamSchema | None = None
    raw_age:int | None = None
    mlbam_id:str | None = None
    fg_id:str | None = None

    
class PaginatedPlayerSchema(Schema):
    results: List[PlayerSchema]
    count: int

class PlayerFilterSchema(FilterSchema):
    search: Optional[str] = ""
    positions: Optional[List[str]] = None
    year: Optional[str] = '2023'

    def filter(self, queryset):
        combined = Q()
        if self.search:
            # Create a Q object for filtering by name
            combined |= Q(name__icontains=self.search)

        if self.positions:
            # Create a list of Q objects for filtering by positions
            position_matches = [Q(positions__icontains=position) for position in self.positions]
            # Combine the list of Q objects using OR operator
            combined = Q(combined, Q(*position_matches, _connector=Q.OR), _connector=Q.AND)

        if self.search or self.positions:
            # Filter the queryset using the combined Q objects
            queryset = queryset.filter(combined)
        
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
    year: int | None = None

    # def __init__(self):
    #     super().__init__()


    @classmethod
    def from_instance(cls, instance: SeasonBattingStatLine):
        new_instance = cls()
        for field_name in FAN_CATEGORIES_HIT:
            setattr(new_instance, f'{field_name}',getattr(instance,f'{field_name}'))
            setattr(new_instance, f'FAN_{field_name}',getattr(instance,f'FAN_{field_name}'))
        new_instance.FAN_total=instance.FAN_total
        new_instance.player_name=instance.player.name if instance.player else None
        new_instance.year=instance.year if instance.year else None
        return new_instance

class PaginatedSeasonBattingStatLineSchema(Schema):
    results: List[SeasonBattingStatLineSchema]
    count: int

class PitchingStatlineSchema(ModelSchema):
    class Meta:
        model = PitchingStatLine
        fields = '__all__'

@api_controller('')
class MyAPIController:
    @api.get("/player", response=PlayerSchema)
    @api.get("/player/{playerid}", response=PlayerSchema)
    def player(request, playerid: str):
        return get_object_or_404(Player.objects.all(), fg_id=playerid)
    
    @api.get("/player/{playerid}/season/{year}", response=SeasonBattingStatLineSchema)
    def season(request, playerid: str, year:str):
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)
        return get_object_or_404(SeasonBattingStatLine.objects.all(), player=player, year=year)

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
    
    @api.get("/players/{year}", response=PaginatedSeasonBattingStatLineSchema)
    def player_seasons(request, year:str, page: int = 1, page_size: int = 50):
        queryset = SeasonBattingStatLine.objects.all().filter(year=year).order_by('-FAN_total')

        paginator = Paginator([SeasonBattingStatLineSchema.from_instance(season) for season in queryset], per_page=page_size)
        if page < 1 or page > paginator.num_pages:
            return api.create_response(status=404, content={"detail": "Page does not exist."})
        
        paginated_data = paginator.page(page)

        return {
            "results":paginated_data,
            "count":paginator.count
        }




    @api.get("statlines/batting", response=List[BattingStatlineSchema])
    def statlines(request, playerid: str):
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)
        batting_lines = BattingStatLine.objects.all().filter(player=player)
        return batting_lines

    @api.get("statlines/pitching",response=List[PitchingStatlineSchema])
    def statlines(request, playerid: str):
        player = get_object_or_404(Player.objects.all(), fg_id=playerid)
        pitching_lines = PitchingStatLine.objects.all().filter(player=player)
        return pitching_lines

    @api.get("/lineup", response=LineupSchema)
    def lineup(request,team: str):
        team_obj = get_object_or_404(Team.objects.all(),abbreviation=team)
        lineup = get_object_or_404(Lineup.objects.all(),lineup_team=team_obj)
        return lineup

    @api.post('/lineup')
    def updateLineup(request, payload:LineupIn):
        team_obj = get_object_or_404(Team.objects.all(),abbreviation=payload.team)
        lineup = get_object_or_404(Lineup.objects.all(),lineup_team=team_obj)
        
        for attr, value in payload.dict(exclude_unset=True).items():
            print(attr, value)
            if attr != 'team':
                player = get_object_or_404(Player.objects.all(), fg_id=value)
                setattr(lineup, attr, player)
                print(attr, value)
        lineup.save()
        return {"success":True}
        

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
