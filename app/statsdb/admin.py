import json
from django import forms
from django.contrib import admin
from django.utils.html import format_html, format_html_join
from .models import Owner, Team, Player, Lineup, BattingStatLine, PitchingStatLine, SeasonBattingStatLine, SeasonPitchingStatLine, Draft, DraftPick, RosterSnapshot


class DraftOrderWidget(forms.Widget):
    """Drag-and-drop reorderable list widget for the Draft.order JSONField."""

    def render(self, name, value, attrs=None, renderer=None):
        try:
            if isinstance(value, str):
                order = json.loads(value)
            elif isinstance(value, list):
                order = value
            else:
                order = []
        except (json.JSONDecodeError, TypeError):
            order = []

        widget_id = (attrs or {}).get('id', f'id_{name}')
        list_id = f'{widget_id}_list'
        json_value = json.dumps(order)

        items = format_html_join(
            '',
            '<li draggable="true" data-value="{}" style="'
            'padding:6px 14px;margin:3px 0;background:#f8f8f8;border:1px solid #ccc;'
            'border-radius:3px;cursor:grab;user-select:none;display:flex;'
            'align-items:center;gap:8px;max-width:280px;">'
            '<span style="color:#aaa;font-size:16px;">⠿</span>{}'
            '<button type="button" onclick="this.closest(\'li\').remove();'
            'document.getElementById(\'{}\').value=JSON.stringify('
            'Array.from(document.getElementById(\'{}\').querySelectorAll(\'li\')).map(function(li){{return li.dataset.value;}}))'
            ')" style="margin-left:auto;background:none;border:none;color:#c00;'
            'cursor:pointer;font-size:14px;padding:0 2px;">×</button></li>',
            ((abbr, abbr, widget_id, list_id) for abbr in order),
        )

        return format_html(
            '<ul id="{}" style="list-style:none;padding:0;margin:0 0 8px;">{}</ul>'
            '<input type="hidden" name="{}" id="{}" value="{}">'
            '<script>'
            '(function(){{'
            '  var list=document.getElementById("{list_id}");'
            '  var inp=document.getElementById("{widget_id}");'
            '  var dragged;'
            '  function sync(){{'
            '    inp.value=JSON.stringify(Array.from(list.querySelectorAll("li")).map(function(li){{return li.dataset.value;}}))'
            '  }}'
            '  list.addEventListener("dragstart",function(e){{dragged=e.target;e.target.style.opacity=".4"}});'
            '  list.addEventListener("dragend",function(e){{e.target.style.opacity="1"}});'
            '  list.addEventListener("dragover",function(e){{'
            '    e.preventDefault();'
            '    var t=e.target.closest("li");'
            '    if(t&&t!==dragged){{'
            '      var r=t.getBoundingClientRect();'
            '      list.insertBefore(dragged,e.clientY<r.top+r.height/2?t:t.nextSibling);'
            '      sync()'
            '    }}'
            '  }});'
            '}})();'
            '</script>',
            list_id, items, name, widget_id, json_value,
            list_id=list_id, widget_id=widget_id,
        )

    def value_from_datadict(self, data, files, name):
        return data.get(name)


class DraftForm(forms.ModelForm):
    class Meta:
        model = Draft
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].widget = DraftOrderWidget()
        # Auto-populate order with all teams for new drafts
        if not self.instance.pk and not self.data:
            teams = list(Team.objects.values_list('abbreviation', flat=True).order_by('abbreviation'))
            self.initial['order'] = teams

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
        'lineup_OF1', 'lineup_OF2', 'lineup_OF3', 'lineup_OF4', 'lineup_OF5',
        'lineup_DH', 'lineup_UTIL',
        'lineup_SP1', 'lineup_SP2', 'lineup_SP3', 'lineup_SP4', 'lineup_SP5',
        'lineup_RP1', 'lineup_RP2', 'lineup_RP3',
    )

admin.site.register(Lineup, LineupAdmin)


class DraftPickInline(admin.TabularInline):
    model = DraftPick
    extra = 0
    raw_id_fields = ('player',)

class DraftAdmin(admin.ModelAdmin):
    form = DraftForm
    list_display = ('year', 'status', 'current_pick', 'rounds')
    inlines = [DraftPickInline]

admin.site.register(Draft, DraftAdmin)
admin.site.register(DraftPick)


class RosterSnapshotAdmin(admin.ModelAdmin):
    list_display = ('date', 'player', 'team')
    list_filter = ('date', 'team')
    search_fields = ('player__name',)
    raw_id_fields = ('player',)
    date_hierarchy = 'date'

admin.site.register(RosterSnapshot, RosterSnapshotAdmin)
