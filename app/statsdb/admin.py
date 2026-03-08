from django.contrib import admin
from .models import Owner, Team, Player, Lineup, BattingStatLine, PitchingStatLine, SeasonBattingStatLine, SeasonPitchingStatLine, Draft, DraftPick
# Register your models here.

class BattingStatLineInline(admin.TabularInline):
    model = BattingStatLine

class PitchingStatLineInline(admin.TabularInline):
    model = PitchingStatLine

class BattingStatlineAdmin(admin.ModelAdmin):
    list_display = ('date','player','ab','h','bb','k')
class PitchingStatlineAdmin(admin.ModelAdmin):
    list_display = ('date','player','ip','r','er','k','h','bb')

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name','position')
    search_fields = ['name','mlbam_id']
    inlines = [BattingStatLineInline,PitchingStatLineInline]

admin.site.register(Owner)
admin.site.register(Team)
admin.site.register(Player, PlayerAdmin)
admin.site.register(BattingStatLine, BattingStatlineAdmin)
admin.site.register(PitchingStatLine,PitchingStatlineAdmin)
admin.site.register(SeasonBattingStatLine)
admin.site.register(SeasonPitchingStatLine)


class LineupAdmin(admin.ModelAdmin):
    list_display = ('lineup_team',)
    raw_id_fields = (
        'lineup_C', 'lineup_1B', 'lineup_2B', 'lineup_SS', 'lineup_3B',
        'lineup_LF', 'lineup_CF', 'lineup_RF',
        'lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5',
        'lineup_RP1', 'lineup_RP2', 'lineup_RP3',
    )

admin.site.register(Lineup, LineupAdmin)


class DraftPickInline(admin.TabularInline):
    model = DraftPick
    extra = 0
    raw_id_fields = ('player',)

class DraftAdmin(admin.ModelAdmin):
    list_display = ('year', 'status', 'current_pick', 'rounds')
    inlines = [DraftPickInline]

admin.site.register(Draft, DraftAdmin)
admin.site.register(DraftPick)
