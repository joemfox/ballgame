from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets, generics
from .api import api

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
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', views.login_view, name='api-login'),
    path('api/logout/', views.logout_view, name='api-logout'),
    path('api/session/', views.session_view, name='api-session'),
    path('api/whoami/', views.whoami_view, name='api-whoami'),
    path('api/change-password/', views.change_password_view, name='api-change-password'),
    path('api/', api.urls),
]