from django import forms
from .models import Player, Game, LineupEntry, AtBat, Pitch

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'jersey_number', 'position', 'is_active']

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['date', 'opponent', 'is_home', 'notes']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

class LineupEntryForm(forms.ModelForm):
    class Meta:
        model = LineupEntry
        fields = ['player', 'batting_order', 'position']

class AtBatForm(forms.ModelForm):
    class Meta:
        model = AtBat
        fields = ['player', 'inning', 'result', 'rbi', 'runs_scored']

class PitchForm(forms.ModelForm):
    class Meta:
        model = Pitch
        fields = ['pitch_type', 'result', 'velocity', 'balls_before', 'strikes_before']

class FinalScoreForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['our_score', 'opponent_score', 'is_complete']