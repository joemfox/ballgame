from ninja import Schema
from .models import Player

class PlayerSchema(Schema):
    name: str
    positions:str
    raw_age:int
    mlbam_id:str
    fg_id:str