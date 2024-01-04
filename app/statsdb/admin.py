from django.contrib import admin
from .models import Owner, Team, Player, BattingStatLine, PitchingStatLine
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

class TeamAdmin(admin.ModelAdmin):
    readonly_fields = ['get_lineup']

admin.site.register(Owner)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(BattingStatLine, BattingStatlineAdmin)
admin.site.register(PitchingStatLine,PitchingStatlineAdmin)
