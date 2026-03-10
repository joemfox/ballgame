import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

@ensure_csrf_cookie
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

@require_POST
def change_password_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Not authenticated."}, status=401)
    data = json.loads(request.body)
    current = data.get("current_password")
    new = data.get("new_password")
    if not current or not new:
        return JsonResponse({"detail": "Both current and new password are required."}, status=400)
    if not request.user.check_password(current):
        return JsonResponse({"detail": "Current password is incorrect."}, status=400)
    if len(new) < 8:
        return JsonResponse({"detail": "New password must be at least 8 characters."}, status=400)
    request.user.set_password(new)
    request.user.save()
    login(request, request.user)
    return JsonResponse({"detail": "Password changed."})

def whoami_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"isAuthenticated": False})
    team = None
    try:
        team = request.user.team.abbreviation
    except Exception:
        pass
    return JsonResponse({"username": request.user.username, "team": team, "is_staff": request.user.is_staff})
