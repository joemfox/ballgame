from rest_framework import serializers
from .models import Player, Team, Owner, BattingStatLine, PitchingStatLine

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('first_name','last_name','team','stats')