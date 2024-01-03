from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets, generics

from . import views

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^api/players/$',views.PlayerList.as_view()),
    re_path(r'^api/teams/$',views.TeamList.as_view()),
    re_path(r'^api/players/([0-9])$',views.player_detail),
    path('api/add-player',views.add_player_to_team),
    path('admin/',admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
]