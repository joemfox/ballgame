from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions, generics

from .models import Team, Player
from .serializers import *

@permission_classes((permissions.AllowAny,))
class PlayerList(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
        

@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def player_detail(request,id):
    try:
        player = Player.objects.get(mlbamid=id)
    except Player.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = PlayerSerializer(player, context={'request': request})
    return Response(serializer.data)