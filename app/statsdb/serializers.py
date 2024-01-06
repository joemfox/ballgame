from rest_framework import serializers
from .models import Player, Team, Lineup, Owner, BattingStatLine, PitchingStatLine
import sys

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

class TeamLineupSerializer(serializers.ModelSerializer):
    lineup_team = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )
    position_fields = ["lineup_C", "lineup_1B", "lineup_2B", "lineup_SS", "lineup_3B", "lineup_LF", "lineup_CF", "lineup_RF", "lineup_SP1", "lineup_SP2", "lineup_SP3", "lineup_SP4", "lineup_SP5", "lineup_RP1", "lineup_RP2", "lineup_RP3"]
    class Meta:
        model = Lineup
        exclude = ('active','created','last_modified')
    
    def update(self,instance,validated_data):
        print(validated_data,file=sys.stderr)
        for pos in validated_data:
            setattr(instance,pos,validated_data[pos])
        instance.save()
        return instance