import sys
import datetime
from dateutil.relativedelta import *

from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from nameparser import HumanName
from .settings import POSITIONS_CHOICES, PLAYER_POSITION_CHOICES

class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.__unicode__()
    
class Owner(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    wins = models.IntegerField(blank=True, null=True)
    losses = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return f"{self.name}, {self.email}"

    def team(self):
        return Team.objects.get(owner_obj=self)

class Lineup(BaseModel):
    lineup_team = models.ForeignKey("Team",null=False,on_delete=models.CASCADE)
    lineup_C = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_C")
    lineup_1B = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_1B")
    lineup_2B = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_2B")
    lineup_SS = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_SS")
    lineup_3B = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_3B")
    lineup_LF = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_LF")
    lineup_CF = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_CF")
    lineup_RF = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_RF")
    lineup_SP1 = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_SP1")
    lineup_SP2 = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_SP2")
    lineup_SP3 = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_SP3")
    lineup_SP4 = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_SP4")
    lineup_SP5 = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_SP5")
    lineup_RP1 = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_RP1")
    lineup_RP2 = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_RP2")
    lineup_RP3 = models.ForeignKey("Player",null=True, on_delete=models.SET_NULL, related_name="lineup_RP3")

    def get_C(self):
        try:
            return self.lineup_C__name
        except:
            return 'None'
    def get_1B(self):
        try:
            return self.lineup_1B__name
        except:
            return 'None'
    def get_2B(self):
        try:
            return self.lineup_2B__name
        except:
            return 'None'
    def get_SS(self):
        try:
            return self.lineup_SS__name
        except:
            return 'None'
    def get_3B(self):
        try:
            return self.lineup_3B__name
        except:
            return 'None'
    def get_LF(self):
        try:
            return self.lineup_LF__name
        except:
            return 'None'
    def get_CF(self):
        try:
            return self.lineup_CF__name
        except:
            return 'None'
    def get_RF(self):
        try:
            return self.lineup_RF__name
        except:
            return 'None'
    def get_SP1(self):
        try:
            return self.lineup_SP1__name
        except:
            return 'None'
    def get_SP2(self):
        try:
            return self.lineup_SP2__name
        except:
            return 'None'
    def get_SP3(self):
        try:
            return self.lineup_SP3__name
        except:
            return 'None'
    def get_SP4(self):
        try:
            return self.lineup_SP4__name
        except:
            return 'None'
    def get_SP5(self):
        try:
            return self.lineup_SP5__name
        except:
            return 'None'
    def get_RP1(self):
        try:
            return self.lineup_RP1__name
        except:
            return 'None'
    def get_RP2(self):
        try:
            return self.lineup_RP2__name
        except:
            return 'None'
    def get_RP3(self):
        try:
            return self.lineup_RP3__name
        except:
            return 'None'

    def get_team(self):
        try:
            return self.lineup_team
        except:
            return None

    def __unicode__(self):
        return f'${self.get_team()}-lineup'
    
class Team(BaseModel):
    city = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=3)
    nickname = models.CharField(max_length=255)
    division = models.CharField(max_length=255, null=True, blank=True)
    owner_obj = models.ForeignKey(
        Owner, on_delete=models.SET_NULL, null=True, blank=True
    )
    owner = models.CharField(max_length=255, null=True, blank=True)
    owner_email = models.CharField(max_length=255, null=True, blank=True)
    championships = ArrayField(models.CharField(max_length=4), blank=True, null=True)

    # lineup slots
    team_lineup = models.ForeignKey("Lineup",blank=True,null=True,on_delete=models.SET_NULL)

    class Meta:
        ordering = ["abbreviation"]

    def __unicode__(self):
        return self.abbreviation

    def to_api_obj(self):
        payload = {
            "city": self.city,
            "abbreviation": self.abbreviation,
            "nickname": self.nickname,
            "division": self.division,
            "owner": self.owner,
            "owner_email": self.owner_email,
        }
        return payload

    def players(self):
        """
        List of Player models associated with this team.
        """
        return Player.objects.filter(team_assigned=self)
    
    # create new lineup when team is saved if it doesn't have one yet
    @transaction.atomic
    def save(self, *args, **kwargs):
        if len(Lineup.objects.filter(lineup_team=self)) == 0:
            lineup, _ = Lineup.objects.get_or_create(lineup_team=self)
            self.team_lineup = lineup
        super(Team,self).save(*args,**kwargs)
    
class Player(BaseModel):

    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    positions = ArrayField(
        models.CharField(max_length=2,null=True, choices=POSITIONS_CHOICES)
    )
    position = models.CharField(
        max_length=255, null=True, choices=PLAYER_POSITION_CHOICES
    )
    birthdate = models.DateField(blank=True, null=True)
    birthdate_qa = models.BooleanField(default=False)
    raw_age = models.IntegerField(default=None, blank=True, null=True)

    # IDENTIFIERS
    mlbam_id = models.CharField(max_length=255, blank=True, null=True)
    mlb_dotcom = models.CharField(max_length=255, blank=True, null=True)
    bref_id = models.CharField(max_length=255, blank=True, null=True)
    fg_id = models.CharField(max_length=255, blank=True, null=False,primary_key=True)

    # LINKS TO THE WEB
    bref_url = models.CharField(max_length=255, blank=True, null=True)
    bref_img = models.CharField(max_length=255, blank=True, null=True)
    fg_url = models.CharField(max_length=255, blank=True, null=True)
    mlb_dotcom_url = models.CharField(max_length=255, blank=True, null=True)

    # FANTASY
    team_assigned = models.ForeignKey(Team, on_delete=models.SET_NULL, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # STATUS AND SUCH
    is_owned = models.BooleanField(default=False)

    # FANTASY ROSTERS
    is_mlb_roster = models.BooleanField(default=False)
    is_aaa_roster = models.BooleanField(default=False)
    is_35man_roster = models.BooleanField(default=False)

    # FROM LIVE ROSTERS
    is_starter = models.BooleanField(default=False)
    is_bench = models.BooleanField(default=False)
    is_player_pool = models.BooleanField(default=False)
    is_injured = models.BooleanField(default=False)
    injury_description = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    role_type = models.CharField(max_length=255, null=True, blank=True)
    roster_status = models.CharField(max_length=255, null=True, blank=True)
    mlb_org = models.CharField(max_length=255, null=True, blank=True)
    is_mlb40man = models.BooleanField(default=False)
    is_bullpen = models.BooleanField(default=False)
    is_mlb = models.BooleanField(default=False)

    # CAREER STATS (for level)
    cs_pa = models.IntegerField(blank=True, null=True)
    cs_gp = models.IntegerField(blank=True, null=True)
    cs_st = models.IntegerField(blank=True, null=True)
    cs_ip = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)

    stats = models.JSONField(null=True, blank=True)

    def __unicode__(self):
        if self.get_team():
            return "%s (%s)" % (self.name, self.get_team().abbreviation)
        return self.name
    
    def set_stats(self, stats_dict):
        if not self.stats:
            self.stats = {}

        if type(self.stats) is not dict:
            self.stats = {}

        self.stats[stats_dict["slug"]] = stats_dict

    @property
    def mlb_image_url(self):
        if self.mlbam_id:
            return f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{self.mlbam_id}/headshot/67/current"
        return None

    @property
    def mlb_url(self):
        if self.mlbam_id:
            return f"https://www.mlb.com/player/{self.mlbam_id}/"
        return None

    @property
    def mlb_api_url(self):
        if self.mlbam_id:
            return f"https://statsapi.mlb.com/api/v1/people/{self.mlbam_id }"
        return None

    def set_fg_url(self):
        if self.fg_id:
            self.fg_url = (
                "https://www.fangraphs.com/statss.aspx?playerid=%s" % self.fg_id
            )

    @property
    def age(self):
        if self.birthdate:
            now = datetime.datetime.utcnow().date()
            return relativedelta(now, self.birthdate).years
        elif self.raw_age:
            return self.raw_age
        return None

    def get_team(self):
        """
        Defaults to the denormalized team attribute, if it exists.
        """
        if self.team_assigned:
            return self.team_assigned
        return None

    def owner(self):
        """
        Determine who owns this player.
        """
        if self.get_team():
            return self.get_team()
        return None

    def set_name(self):
        """
        Turn first / last into a name or
        """
        if self.first_name and self.last_name:
            name_string = "%s" % self.first_name
            name_string += " %s" % self.last_name
            self.name = name_string

        if self.name:
            if not self.first_name and not self.last_name:
                n = HumanName(self.name)
                self.first_name = n.first
                if n.middle:
                    self.first_name = n.first + " " + n.middle
                self.last_name = n.last
                if n.suffix:
                    self.last_name = n.last + " " + n.suffix

    def set_ids(self):
        if self.fg_url and not self.fg_id:
            if self.fg_url:
                if "?playerid=" in self.fg_url:
                    self.fg_id = self.fg_url.split("?playerid=")[1].split("&")[0]

    def set_owned(self):
            if self.team_assigned == None:
                self.is_owned = False
            else:
                self.is_owned = True
    
    def team_display(self):
        if self.team:
            return self.team.abbreviation
        return None
    
class Membership(BaseModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date_added = models.DateField()
    
class BattingStatLine(BaseModel):
    # id = game_id + player_id
    id = models.CharField(max_length=255,null=False, primary_key=True)

    # game info
    date = models.DateField(null=False)

    # player info
    player = models.ForeignKey(Player,blank=True,null=True,on_delete=models.CASCADE)
    last_name = models.CharField(max_length=255,null=True)
    position = models.CharField(max_length=255,null=True)

    # slashline
    avg = models.DecimalField(max_digits=4,decimal_places=3, blank=True,null=True)
    obp = models.DecimalField(max_digits=4,decimal_places=3, blank=True,null=True)
    slg = models.DecimalField(max_digits=4,decimal_places=3, blank=True,null=True)

    # game stats (from boxscore)
    batting_order = models.IntegerField(blank=True,null=True)
    ab = models.IntegerField(blank=True,null=True)
    r = models.IntegerField(blank=True,null=True)
    h = models.IntegerField(blank=True,null=True)
    doubles = models.IntegerField(blank=True,null=True)
    triples = models.IntegerField(blank=True,null=True)
    hr = models.IntegerField(blank=True,null=True)
    rbi = models.IntegerField(blank=True,null=True)
    bb = models.IntegerField(blank=True,null=True)
    k = models.IntegerField(blank=True,null=True)
    lob = models.IntegerField(blank=True,null=True)
    sb = models.IntegerField(blank=True,null=True)

    # game stats (from elsewhere)
    cs = models.IntegerField(blank=True,null=True)
    e = models.IntegerField(blank=True,null=True)
    # runners in scoring position left on base with 2 outs
    assblood = models.IntegerField(blank=True,null=True)

    def __unicode__(self):
        if self.player:
            return f'{self.date} - {self.player.name}'
        else:
            return f'{self.date} - {self.last_name}'
        return self.name

    def player_display(self):
        if self.player:
            return self.player.name
        return None

class PitchingStatLine(BaseModel):
    # id = game_id + player_id
    id = models.CharField(max_length=255,null=False,primary_key=True)

    # game info
    date = models.DateField(null=False)

    # player info
    player = models.ForeignKey(Player,blank=True,null=True,on_delete=models.SET_NULL)
    last_name = models.CharField(max_length=255,null=True)
    position = models.CharField(max_length=255,null=True)

    # game stats (from boxscore)
    ip = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    h = models.IntegerField(blank=True,null=True)
    r = models.IntegerField(blank=True,null=True)
    er = models.IntegerField(blank=True,null=True)
    bb = models.IntegerField(blank=True,null=True)
    k = models.IntegerField(blank=True,null=True)
    hr = models.IntegerField(blank=True,null=True)

    # game stats (from elsewhere)
    bf = models.IntegerField(blank=True,null=True)
    balks = models.IntegerField(blank=True,null=True)
    qs = models.BooleanField(null=True)
    perfect_game = models.BooleanField(null=True)
    no_hitter= models.BooleanField(null=True)
    
    def player_display(self):
        if self.player:
            return self.player.name
        return None