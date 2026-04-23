from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db import models
from .models import Player, Game, LineupEntry, AtBat, Pitch
from .forms import PlayerForm, GameForm, LineupEntryForm, AtBatForm, PitchForm, FinalScoreForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    games = Game.objects.filter(created_by=request.user).order_by('-date')[:5]
    players = Player.objects.filter(created_by=request.user, is_active=True)
    total_games = Game.objects.filter(created_by=request.user, is_complete=True)
    wins = sum(1 for g in total_games if g.result() == 'W')
    losses = sum(1 for g in total_games if g.result() == 'L')
    return render(request, 'core/dashboard.html', {
        'recent_games': games, 'players': players,
        'wins': wins, 'losses': losses, 'total': total_games.count()
    })

@login_required
def roster(request):
    players = Player.objects.filter(created_by=request.user)
    return render(request, 'core/roster.html', {'players': players})

@login_required
def add_player(request):
    form = PlayerForm(request.POST or None)
    if form.is_valid():
        player = form.save(commit=False)
        player.created_by = request.user
        player.save()
        return redirect('roster')
    return render(request, 'core/player_form.html', {'form': form, 'title': 'Add Player'})

@login_required
def edit_player(request, pk):
    player = get_object_or_404(Player, pk=pk, created_by=request.user)
    form = PlayerForm(request.POST or None, instance=player)
    if form.is_valid():
        form.save()
        return redirect('roster')
    return render(request, 'core/player_form.html', {'form': form, 'title': 'Edit Player'})

@login_required
def delete_player(request, pk):
    player = get_object_or_404(Player, pk=pk, created_by=request.user)
    if request.method == 'POST':
        player.delete()
        return redirect('roster')
    return render(request, 'core/confirm_delete.html', {'obj': player})

@login_required
def game_list(request):
    games = Game.objects.filter(created_by=request.user)
    return render(request, 'core/game_list.html', {'games': games})

@login_required
def new_game(request):
    form = GameForm(request.POST or None)
    if form.is_valid():
        game = form.save(commit=False)
        game.created_by = request.user
        game.save()
        return redirect('lineup', game_id=game.pk)
    return render(request, 'core/game_form.html', {'form': form})

@login_required
def lineup(request, game_id):
    game = get_object_or_404(Game, pk=game_id, created_by=request.user)
    players = Player.objects.filter(created_by=request.user, is_active=True)
    entries = LineupEntry.objects.filter(game=game)
    if request.method == 'POST':
        LineupEntry.objects.filter(game=game).delete()
        for i in range(1, 10):
            player_id = request.POST.get(f'player_{i}')
            position = request.POST.get(f'position_{i}')
            if player_id:
                LineupEntry.objects.create(
                    game=game,
                    player_id=player_id,
                    batting_order=i,
                    position=position or 'P'
                )
        return redirect('record_game', game_id=game.pk)
    return render(request, 'core/lineup.html', {
        'game': game, 'players': players, 'entries': entries,
        'spots': range(1, 10)
    })

@login_required
def record_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id, created_by=request.user)
    lineup_entries = LineupEntry.objects.filter(game=game).select_related('player')
    at_bats = AtBat.objects.filter(game=game).select_related('player').prefetch_related('pitches')
    current_ab = at_bats.filter(result='').last()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'new_at_bat':
            player_id = request.POST.get('player_id')
            inning = request.POST.get('inning', 1)
            AtBat.objects.create(
                game=game,
                player_id=player_id,
                inning=inning,
                batting_order_position=request.POST.get('batting_order', 1)
            )
            return redirect('record_game', game_id=game_id)

        elif action == 'add_pitch' and current_ab:
            pitch_count = current_ab.pitches.count()
            Pitch.objects.create(
                at_bat=current_ab,
                pitch_number=pitch_count + 1,
                pitch_type=request.POST.get('pitch_type', 'UN'),
                result=request.POST.get('pitch_result'),
                velocity=request.POST.get('velocity') or None,
                balls_before=request.POST.get('balls', 0),
                strikes_before=request.POST.get('strikes', 0),
            )
            return redirect('record_game', game_id=game_id)

        elif action == 'end_at_bat' and current_ab:
            current_ab.result = request.POST.get('ab_result', 'GO')
            current_ab.rbi = request.POST.get('rbi', 0)
            current_ab.runs_scored = request.POST.get('runs_scored') == 'on'
            current_ab.save()
            return redirect('record_game', game_id=game_id)

        elif action == 'end_game':
            game.our_score = request.POST.get('our_score', 0)
            game.opponent_score = request.POST.get('opponent_score', 0)
            game.is_complete = True
            game.save()
            return redirect('game_summary', game_id=game_id)

    return render(request, 'core/record_game.html', {
        'game': game,
        'lineup': lineup_entries,
        'at_bats': at_bats,
        'current_ab': current_ab,
        'pitch_types': Pitch.PITCH_TYPES,
        'pitch_results': Pitch.RESULTS,
        'ab_results': AtBat.RESULTS,
    })

@login_required
def game_summary(request, game_id):
    game = get_object_or_404(Game, pk=game_id, created_by=request.user)
    at_bats = AtBat.objects.filter(game=game).select_related('player').prefetch_related('pitches')

    batter_lines = []
    for ab in at_bats:
        pitches = list(ab.pitches.all())
        batter_lines.append({
            'player': ab.player,
            'inning': ab.inning,
            'pitches': len(pitches),
            'balls': sum(1 for p in pitches if p.result == 'BALL'),
            'strikes': sum(1 for p in pitches if 'STRIKE' in p.result or p.result == 'FOUL'),
            'result': ab.get_result_display(),
            'rbi': ab.rbi,
            'scored': ab.runs_scored,
        })

    total_pitches = sum(b['pitches'] for b in batter_lines)
    hits = sum(1 for ab in at_bats if ab.result in ['1B','2B','3B','HR'])
    strikeouts = sum(1 for ab in at_bats if ab.result in ['K','KL'])
    walks = sum(1 for ab in at_bats if ab.result == 'BB')

    return render(request, 'core/game_summary.html', {
        'game': game,
        'batter_lines': batter_lines,
        'total_pitches': total_pitches,
        'hits': hits,
        'strikeouts': strikeouts,
        'walks': walks,
    })

@login_required
def player_stats(request, pk):
    player = get_object_or_404(Player, pk=pk, created_by=request.user)
    all_abs = AtBat.objects.filter(player=player, game__is_complete=True).select_related('game')

    total_abs = all_abs.exclude(result__in=['BB','HBP','']).count()
    hits = all_abs.filter(result__in=['1B','2B','3B','HR']).count()
    doubles = all_abs.filter(result='2B').count()
    triples = all_abs.filter(result='3B').count()
    homers = all_abs.filter(result='HR').count()
    walks = all_abs.filter(result='BB').count()
    strikeouts = all_abs.filter(result__in=['K','KL']).count()
    rbi = sum(ab.rbi for ab in all_abs)
    runs = all_abs.filter(runs_scored=True).count()
    avg = round(hits / total_abs, 3) if total_abs > 0 else 0.000

    game_logs = []
    for ab in all_abs:
        game_logs.append({
            'game': ab.game,
            'result': ab.get_result_display(),
            'rbi': ab.rbi,
            'scored': ab.runs_scored,
            'pitches': ab.pitches.count(),
        })

    return render(request, 'core/player_stats.html', {
        'player': player,
        'avg': avg, 'hits': hits, 'total_abs': total_abs,
        'doubles': doubles, 'triples': triples, 'homers': homers,
        'walks': walks, 'strikeouts': strikeouts,
        'rbi': rbi, 'runs': runs,
        'game_logs': game_logs,
    })
