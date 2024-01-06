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
from .serializers import *

class PlayerFilter(django_filters.FilterSet):
    # filter for players by position, even if they have more positions available
    base_field_class = SimpleArrayField
    positions = django_filters.MultipleChoiceFilter(field_name="positions",choices=POSITIONS_CHOICES, method="filter_positions")

    def filter_positions(self, queryset, name, value):
        return queryset.filter(positions__overlap=value)
    
    class Meta:
        model = Player
        fields = ['positions']

@permission_classes((permissions.AllowAny,))
class PlayerList(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filter_backends = [filters.OrderingFilter,filters.SearchFilter,django_filters.DjangoFilterBackend]
    filterset_class = PlayerFilter
    ordering_fields = ['team','name','first_name','last_name']
    search_fields = ['name']

@permission_classes((permissions.AllowAny,))
class TeamList(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

@permission_classes((permissions.AllowAny,))
class PlayerDetail(viewsets.ModelViewSet):
    queryset = Player.objects.all()

    def retrieve(self, request):
        try:
            fg_id = request.query_params['id']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        player = get_object_or_404(self.queryset, fg_id=fg_id)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)

@api_view(['GET','POST'])
@permission_classes((permissions.AllowAny,))
def lineup_detail(request):
    serializer_class = TeamLineupSerializer

    queryset = Team.objects.all()
    try:
        team_id = request.query_params['team']
        # print(team_id,file=sys.stderr)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    lineup = queryset.filter(abbreviation=team_id).first().get_lineup()
    print(lineup,file=sys.stderr)

    if request.method == 'GET':
        serializer = TeamLineupSerializer(lineup)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        new_lineup_data = request.data
        serializer = TeamLineupSerializer(lineup, data=new_lineup_data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    

@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def player_detail(request):
    print(request.data,file=sys.stderr)
    try:
        player = Player.objects.get(fg_id=request.data['id'])
    except Player.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = PlayerSerializer(player, context={'request': request})
    return Response(serializer.data)

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
    