import datetime
from dateutil.relativedelta import *

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from nameparser import HumanName

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

    # LIVE STATS!
    ls_hits = models.IntegerField(blank=True, null=True)
    ls_2b = models.IntegerField(blank=True, null=True)
    ls_3b = models.IntegerField(blank=True, null=True)
    ls_hr = models.IntegerField(blank=True, null=True)
    ls_sb = models.IntegerField(blank=True, null=True)
    ls_runs = models.IntegerField(blank=True, null=True)
    ls_rbi = models.IntegerField(blank=True, null=True)
    ls_k = models.IntegerField(blank=True, null=True)
    ls_bb = models.IntegerField(blank=True, null=True)
    ls_plate_appearances = models.IntegerField(blank=True, null=True)
    ls_ab = models.IntegerField(blank=True, null=True)
    ls_avg = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    ls_obp = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    ls_slg = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    ls_iso = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    ls_k_pct = models.DecimalField(
        max_digits=4, decimal_places=1, blank=True, null=True
    )
    ls_bb_pct = models.DecimalField(
        max_digits=4, decimal_places=1, blank=True, null=True
    )

    ls_g = models.IntegerField(blank=True, null=True)
    ls_gs = models.IntegerField(blank=True, null=True)
    ls_ip = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    ls_pk = models.IntegerField(blank=True, null=True)
    ls_pbb = models.IntegerField(blank=True, null=True)
    ls_ha = models.IntegerField(blank=True, null=True)
    ls_hra = models.IntegerField(blank=True, null=True)
    ls_er = models.IntegerField(blank=True, null=True)
    ls_k_9 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ls_hits_9 = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True
    )
    ls_bb_9 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ls_hr_9 = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ls_era = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ls_whip = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

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
        return Player.objects.filter(team=self)


class Player(BaseModel):
    PITCHER = "P"
    STARTER = "SP"
    RELIEVER = "RP"
    CATCHER = "C"
    INFIELD = "IF"
    OUTFIELD = "OF"
    FIRSTBASE = "1B"
    SECONDBASE = "2B"
    SHORTSTOP = "SS"
    THIRDBASE = "3B"
    LEFTFIELD = "LF"
    CENTERFIELD = "CF"
    RIGHTFIELD = "RF"
    INFIELD_OUTFIELD = "IF-OF"
    PITCHER_OF = "OF-P"
    PITCHER_IF = "IF-P"
    PLAYER_POSITION_CHOICES = (
        (PITCHER, "Pitcher"),
        (STARTER, "Starter"),
        (RELIEVER, "Reliever"),
        (CATCHER, "Catcher"),
        (INFIELD, "Infield"),
        (OUTFIELD, "Outfield"),
        (FIRSTBASE, "First base"),
        (SECONDBASE, "Second base"),
        (SHORTSTOP, "Shortstop"),
        (THIRDBASE, "Third base"),
        (LEFTFIELD, "Left field"),
        (CENTERFIELD, "Center field"),
        (RIGHTFIELD, "Right field"),
        (INFIELD_OUTFIELD, "IF-OF"),
        (PITCHER_OF, "OF-P"),
        (PITCHER_IF, "IF-P"),
    )
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    positions = ArrayField(
        models.CharField(max_length=2,null=True)
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
    fg_id = models.CharField(max_length=255, blank=True, null=True)

    # LINKS TO THE WEB
    bref_url = models.CharField(max_length=255, blank=True, null=True)
    bref_img = models.CharField(max_length=255, blank=True, null=True)
    fg_url = models.CharField(max_length=255, blank=True, null=True)
    mlb_dotcom_url = models.CharField(max_length=255, blank=True, null=True)

    # FANTASY
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, blank=True, null=True)
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
        if self.team:
            return self.team
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
            if self.team == None:
                self.is_owned = False
            else:
                self.is_owned = True
    
    def team_display(self):
        if self.team:
            return self.team.abbreviation
        return None
    
class BattingStatLine(BaseModel):
    # id = game_id + player_id
    id = models.CharField(max_length=255,null=False, primary_key=True)

    # game info
    date = models.DateField(null=False)

    # player info
    player = models.ForeignKey(Player,blank=True,null=True,on_delete=models.SET_NULL)
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