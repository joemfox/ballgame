from rest_framework import serializers
from .models import Player, Team, Owner, BattingStatLine, PitchingStatLine

class PlayerSerializer(serializers.ModelSerializer):
    team = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )
    class Meta:
        model = Player
        fields = ('fg_id','mlbam_id','name','first_name','last_name','team','stats')

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["city","abbreviation","nickname","division","owner","owner_email"]