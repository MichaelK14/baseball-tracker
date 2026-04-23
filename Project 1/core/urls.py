from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),

    path('roster/', views.roster, name='roster'),
    path('roster/add/', views.add_player, name='add_player'),
    path('roster/<int:pk>/edit/', views.edit_player, name='edit_player'),
    path('roster/<int:pk>/delete/', views.delete_player, name='delete_player'),
    path('roster/<int:pk>/stats/', views.player_stats, name='player_stats'),

    path('games/', views.game_list, name='game_list'),
    path('games/new/', views.new_game, name='new_game'),
    path('games/<int:game_id>/lineup/', views.lineup, name='lineup'),
    path('games/<int:game_id>/record/', views.record_game, name='record_game'),
    path('games/<int:game_id>/summary/', views.game_summary, name='game_summary'),
]