from django.contrib import admin

from .models import Player, Game, LineupEntry, AtBat, Pitch

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['jersey_number', 'last_name', 'first_name', 'position', 'is_active']
    list_filter = ['position', 'is_active']

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['date', 'opponent', 'is_home', 'our_score', 'opponent_score', 'is_complete']
    list_filter = ['is_home', 'is_complete']

@admin.register(LineupEntry)
class LineupEntryAdmin(admin.ModelAdmin):
    list_display = ['game', 'batting_order', 'player', 'position']

@admin.register(AtBat)
class AtBatAdmin(admin.ModelAdmin):
    list_display = ['game', 'player', 'inning', 'result']

@admin.register(Pitch)
class PitchAdmin(admin.ModelAdmin):
    list_display = ['at_bat', 'pitch_number', 'pitch_type', 'result', 'velocity']
