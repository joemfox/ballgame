from rest_framework import serializers
from .models import Player, Team, Owner, BattingStatLine, PitchingStatLine

class PlayerSerializer(serializers.ModelSerializer):
    team_assigned = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )
    class Meta:
        model = Player
        fields = ('fg_id','mlbam_id','name','first_name','last_name','positions','team_assigned','stats')

class TeamSerializer(serializers.ModelSerializer):
    players = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    class Meta:
        model = Team
        fields = ["city","abbreviation","nickname","division","owner","owner_email","players"]