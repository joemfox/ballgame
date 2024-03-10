import datetime
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.forms import SimpleArrayField
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions, generics, filters, viewsets
from django_filters import rest_framework as django_filters
import sys

from .settings import POSITIONS_CHOICES
from .models import Team, Player, Membership

@api_view(['POST'])
# TODO: BUILD REAL PERMISSIONS/LOGINS LOL
@permission_classes((permissions.AllowAny,))
def add_player_to_team(request):
    print(request.data,file=sys.stderr)
    id = request.data['id']
    team_id = request.data['team_id']
    try:
        player = Player.objects.get(fg_id=id)
        team = Team.objects.get(abbreviation=team_id)
    except Player.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND,data="Player not found")
    except Team.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND,data="Team not found")
    
    membership = Membership(
        player=player,
        team=team,
        date_added=datetime.datetime.now()
    )

    membership.save()

    player.set_owned()
    player.team_assigned = team
    player.save()
    serializer = PlayerSerializer(player)
    return Response(status=status.HTTP_200_OK,data=serializer.data)
    