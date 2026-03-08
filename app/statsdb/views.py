from django.shortcuts import render

import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

@require_POST
def login_view(request):
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")
    
    if username is None or password is None:
        return JsonResponse({"detail":"Please provide username and password"})
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"detail":"invalid credentials"}, status=400)
    login(request, user)
    return JsonResponse({"details": "Succesfully logged in!"})

def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail":"You are not logged in!"}, status=400)
    logout(request)
    return JsonResponse({"detail":"Succesfully logged out!"})


@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"isAuthenticated": False})
    return JsonResponse({"isAuthenticated": True})

def whoami_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"isAuthenticated": False})
    team = None
    try:
        team = request.user.team.abbreviation
    except Exception:
        pass
    return JsonResponse({"username": request.user.username, "team": team, "is_staff": request.user.is_staff})

# @api_view(['POST'])
# # TODO: BUILD REAL PERMISSIONS/LOGINS LOL
# @permission_classes((permissions.AllowAny,))
# def add_player_to_team(request):
#     print(request.data,file=sys.stderr)
#     id = request.data['id']
#     team_id = request.data['team_id']
#     try:
#         player = Player.objects.get(fg_id=id)
#         team = Team.objects.get(abbreviation=team_id)
#     except Player.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND,data="Player not found")
#     except Team.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND,data="Team not found")
    
#     membership = Membership(
#         player=player,
#         team=team,
#         date_added=datetime.datetime.now()
#     )

#     membership.save()

#     player.set_owned()
#     player.team_assigned = team
#     player.save()
#     serializer = PlayerSerializer(player)
#     return Response(status=status.HTTP_200_OK,data=serializer.data)
    