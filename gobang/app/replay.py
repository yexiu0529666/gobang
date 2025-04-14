from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Game, User

bp = Blueprint('replay', __name__)

@bp.route('/api/replays')
@login_required
def get_replays():
    # 获取当前用户参与的所有游戏
    games = Game.query.filter(
        (Game.player1_id == current_user.id) | 
        (Game.player2_id == current_user.id)
    ).order_by(Game.start_time.desc()).all()
    
    replays = []
    for game in games:
        # 跳过只有一个玩家的游戏（未开始的游戏）
        if not game.player2_id:
            continue
        
        white_player = {
            'id': game.player2.id,
            'username': game.player2.username
        }
        
        # 获取棋局的所有步骤
        moves_list = []
        for move in game.moves.all():
            moves_list.append({
                'id': move.id,
                'player_id': move.player_id,
                'x': move.x,
                'y': move.y,
                'timestamp': move.timestamp.isoformat(),
                'move_number': move.move_number
            })
            
        replays.append({
            'id': game.id,
            'black_player': {
                'id': game.player1.id,
                'username': game.player1.username
            },
            'white_player': white_player,
            'winner': {
                'id': game.winner.id,
                'username': game.winner.username
            } if game.winner else None,
            'start_time': game.start_time.isoformat(),
            'end_time': game.end_time.isoformat() if game.end_time else None,
            'moves': moves_list
        })
    
    return jsonify(replays)

@bp.route('/api/replay/<int:game_id>')
def get_replay(game_id):
    game = Game.query.get_or_404(game_id)
    
    # 如果游戏只有一个玩家，则返回404
    if not game.player2_id:
        return jsonify({'error': '该对局尚未开始或不存在'}), 404
    
    white_player = {
        'id': game.player2.id,
        'username': game.player2.username
    }
    
    # 获取棋局的所有步骤
    moves_list = []
    for move in game.moves.all():
        moves_list.append({
            'id': move.id,
            'player_id': move.player_id,
            'x': move.x,
            'y': move.y,
            'timestamp': move.timestamp.isoformat(),
            'move_number': move.move_number
        })
    
    return jsonify({
        'id': game.id,
        'black_player': {
            'id': game.player1.id,
            'username': game.player1.username
        },
        'white_player': white_player,
        'winner': {
            'id': game.winner.id,
            'username': game.winner.username
        } if game.winner else None,
        'start_time': game.start_time.isoformat(),
        'end_time': game.end_time.isoformat() if game.end_time else None,
        'moves': moves_list
    })

@bp.route('/api/leaderboard')
def get_leaderboard():
    # 获取积分最高的前50名玩家
    top_players = User.query.order_by(User.rating.desc()).limit(50).all()
    
    leaderboard = []
    for player in top_players:
        total_games = player.wins + player.losses + player.draws
        leaderboard.append({
            'id': player.id,
            'username': player.username,
            'rating': player.rating,
            'games_won': player.wins,
            'total_games': total_games,
            'win_rate': (player.wins / total_games * 100) if total_games > 0 else 0
        })
    
    return jsonify(leaderboard) 