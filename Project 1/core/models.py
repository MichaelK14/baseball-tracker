from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    POSITIONS = [
        ('P', 'Pitcher'), ('C', 'Catcher'), ('1B', 'First Base'),
        ('2B', 'Second Base'), ('3B', 'Third Base'), ('SS', 'Shortstop'),
        ('LF', 'Left Field'), ('CF', 'Center Field'), ('RF', 'Right Field'),
        ('DH', 'Designated Hitter'),
    ]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    jersey_number = models.IntegerField(unique=True)
    position = models.CharField(max_length=3, choices=POSITIONS)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"#{self.jersey_number} {self.first_name} {self.last_name}"

    def batting_average(self):
        abs_ = AtBat.objects.filter(player=self, game__is_complete=True)
        hits = abs_.filter(result__in=['1B','2B','3B','HR']).count()
        total = abs_.exclude(result__in=['BB','HBP','']).count()
        return round(hits / total, 3) if total > 0 else 0.000

    class Meta:
        ordering = ['jersey_number']


class Game(models.Model):
    date = models.DateField()
    opponent = models.CharField(max_length=100)
    is_home = models.BooleanField(default=True)
    our_score = models.IntegerField(default=0)
    opponent_score = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        location = 'vs' if self.is_home else '@'
        return f"{self.date} {location} {self.opponent}"

    def result(self):
        if not self.is_complete:
            return 'In Progress'
        if self.our_score > self.opponent_score:
            return 'W'
        elif self.our_score < self.opponent_score:
            return 'L'
        return 'T'

    class Meta:
        ordering = ['-date']


class LineupEntry(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='lineup')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    batting_order = models.IntegerField()
    position = models.CharField(max_length=3)

    class Meta:
        ordering = ['batting_order']
        unique_together = ['game', 'batting_order']

    def __str__(self):
        return f"{self.batting_order}. {self.player}"


class AtBat(models.Model):
    RESULTS = [
        ('', 'In Progress'),
        ('1B', 'Single'), ('2B', 'Double'), ('3B', 'Triple'), ('HR', 'Home Run'),
        ('BB', 'Walk'), ('HBP', 'Hit by Pitch'),
        ('K', 'Strikeout'), ('KL', 'Strikeout Looking'),
        ('GO', 'Ground Out'), ('FO', 'Fly Out'), ('LO', 'Line Out'),
        ('SAC', 'Sacrifice'), ('FC', "Fielder's Choice"), ('E', 'Error'),
    ]
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='at_bats')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='at_bats')
    inning = models.IntegerField()
    batting_order_position = models.IntegerField(default=1)
    result = models.CharField(max_length=4, choices=RESULTS, blank=True, default='')
    rbi = models.IntegerField(default=0)
    runs_scored = models.BooleanField(default=False)

    class Meta:
        ordering = ['inning', 'batting_order_position']


class Pitch(models.Model):
    PITCH_TYPES = [
        ('FB', 'Fastball'), ('CB', 'Curveball'), ('SL', 'Slider'),
        ('CH', 'Changeup'), ('CT', 'Cutter'), ('SI', 'Sinker'), ('UN', 'Unknown'),
    ]
    RESULTS = [
        ('BALL', 'Ball'), ('STRIKE_S', 'Strike Swinging'),
        ('STRIKE_L', 'Strike Looking'), ('FOUL', 'Foul Ball'),
        ('IN_PLAY', 'In Play'),
    ]
    at_bat = models.ForeignKey(AtBat, on_delete=models.CASCADE, related_name='pitches')
    pitch_number = models.IntegerField()
    pitch_type = models.CharField(max_length=2, choices=PITCH_TYPES, default='UN')
    result = models.CharField(max_length=10, choices=RESULTS)
    velocity = models.IntegerField(null=True, blank=True)
    balls_before = models.IntegerField(default=0)
    strikes_before = models.IntegerField(default=0)

    class Meta:
        ordering = ['pitch_number']
