from http import HTTPStatus
from typing import List
from django.core.exceptions import (
    FieldError,
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError,
)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Player, Team, Lineup, BattingStatLine, PitchingStatLine
from ninja import NinjaAPI, Schema, ModelSchema
from ninja.pagination import paginate, PageNumberPagination
from ninja.errors import ValidationError as NinjaValidationError


api = NinjaAPI()

class TeamSchema(Schema):
    # city:str 
    abbreviation:str = None
    # nickname:str


class PlayerSchema(Schema):
    name: str
    first_name: str = None
    last_name: str = None
    positions:List[str]
    team_assigned: TeamSchema = None
    raw_age:int
    mlbam_id:str
    fg_id:str

class LineupSchema(ModelSchema):
        class Meta:
            model = Lineup
            fields = ["lineup_C", "lineup_1B", "lineup_2B", "lineup_SS", "lineup_3B", "lineup_LF", "lineup_CF", "lineup_RF", "lineup_SP1", "lineup_SP2", "lineup_SP3", "lineup_SP4", "lineup_SP5", "lineup_RP1", "lineup_RP2", "lineup_RP3"]
            fields_optional = '__all__'

class LineupIn(Schema):
        team:str
        lineup_C: str = None
        lineup_1B: str = None
        lineup_2B: str = None
        lineup_SS: str = None
        lineup_3B: str = None
        lineup_LF: str = None
        lineup_CF: str = None
        lineup_RF: str = None
        lineup_SP1: str = None
        lineup_SP2: str = None
        lineup_SP3: str = None
        lineup_SP4: str = None
        lineup_SP5: str = None
        lineup_RP1: str = None
        lineup_RP2: str = None
        lineup_RP3: str = None

class BattingStatlineSchema(ModelSchema):
    class Meta:
        model = BattingStatLine
        fields = '__all__'

class PitchingStatlineSchema(ModelSchema):
    class Meta:
        model = PitchingStatLine
        fields = '__all__'


@api.get("/player", response=PlayerSchema)
def player(request, playerid: str):
    return get_object_or_404(Player.objects.all(), fg_id=playerid)

@api.get("/players", response=List[PlayerSchema])
@paginate(PageNumberPagination)
def players(request):
    return Player.objects.all()

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
