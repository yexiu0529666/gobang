from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Game, Move, Match, User
from datetime import datetime

bp = Blueprint('game', __name__)

@bp.route('/api/matches/check', methods=['GET'])
@login_required
def check_matches():
    # 查询是否有等待中的匹配
    waiting_match = Match.query.filter_by(
        status='waiting'
    ).filter(
        Match.player1_id != current_user.id
    ).first()
    
    if waiting_match:
        return jsonify({
            'status': 'match_found',
            'match_id': waiting_match.id,
            'player1_id': waiting_match.player1_id,
            'player1_username': User.query.get(waiting_match.player1_id).username
        }), 200
    else:
        return jsonify({
            'status': 'no_match_found'
        }), 200

@bp.route('/api/matches/create', methods=['POST'])
@login_required
def create_match():
    # 创建一个新的匹配
    match = Match(
        player1_id=current_user.id,
        status='waiting'
    )
    
    # 创建一个新的游戏
    game = Game(
        player1_id=current_user.id,
        status='waiting'
    )
    
    db.session.add(game)
    db.session.flush()  # 刷新会话以获取 game.id
    
    match.game_id = game.id
    db.session.add(match)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'match_id': match.id,
        'game_id': game.id
    }), 201

@bp.route('/api/matches/join/<int:match_id>', methods=['POST'])
@login_required
def join_match(match_id):
    match = Match.query.get_or_404(match_id)
    
    if match.status != 'waiting':
        return jsonify({
            'status': 'error',
            'message': '该匹配已经关闭'
        }), 400
    
    if match.player1_id == current_user.id:
        return jsonify({
            'status': 'error',
            'message': '不能加入自己创建的匹配'
        }), 400
    
    # 更新匹配状态
    match.player2_id = current_user.id
    match.status = 'closed'
    
    # 更新游戏状态
    game = Game.query.get(match.game_id)
    game.player2_id = current_user.id
    game.status = 'playing'
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'game_id': game.id
    }), 200

@bp.route('/api/matches/cancel/<int:match_id>', methods=['POST'])
@login_required
def cancel_match(match_id):
    match = Match.query.get_or_404(match_id)
    
    if match.player1_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': '只有创建者可以取消匹配'
        }), 400
    
    if match.status != 'waiting':
        return jsonify({
            'status': 'error',
            'message': '该匹配已经关闭'
        }), 400
    
    # 更新匹配状态
    match.status = 'closed'
    
    # 更新游戏状态
    game = Game.query.get(match.game_id)
    game.status = 'abandoned'
    
    db.session.commit()
    
    return jsonify({
        'status': 'success'
    }), 200

@bp.route('/api/matches/<int:match_id>', methods=['GET'])
@login_required
def get_match(match_id):
    match = Match.query.get_or_404(match_id)
    
    # 检查用户是否有权限查看该匹配
    if match.player1_id != current_user.id and match.player2_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': '没有权限查看该匹配'
        }), 403
    
    player2 = User.query.get(match.player2_id) if match.player2_id else None
    
    return jsonify({
        'id': match.id,
        'player1_id': match.player1_id,
        'player2_id': match.player2_id,
        'player2_username': player2.username if player2 else None,
        'game_id': match.game_id,
        'status': match.status
    }), 200

@bp.route('/api/games/<int:game_id>', methods=['GET'])
@login_required
def get_game(game_id):
    game = Game.query.get_or_404(game_id)

    # 检查用户是否有权限查看该游戏
    if game.player1_id != current_user.id and game.player2_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': '没有权限查看该对局'
        }), 403
    
    # 获取游戏的所有棋步
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
    
    # 获取玩家信息
    player1 = User.query.get(game.player1_id)
    player2 = User.query.get(game.player2_id) if game.player2_id else None
    winner = User.query.get(game.winner_id) if game.winner_id else None
    
    return jsonify({
        'id': game.id,
        'player1_id': game.player1_id,
        'player1_username': player1.username,
        'player2_id': game.player2_id,
        'player2_username': player2.username if player2 else None,
        'start_time': game.start_time.isoformat(),
        'end_time': game.end_time.isoformat() if game.end_time else None,
        'winner_id': game.winner_id,
        'winner_username': winner.username if winner else None,
        'moves': moves_list,
        'status': game.status,
        'time_limit': game.time_limit,
        'current_player_id': game.player1_id if len(moves_list) % 2 == 0 else game.player2_id
    }), 200

@bp.route('/api/games/<int:game_id>/move', methods=['POST'])
@login_required
def make_move(game_id):
    game = Game.query.get_or_404(game_id)
    
    # 检查游戏是否在进行中
    if game.status != 'playing':
        return jsonify({
            'status': 'error',
            'message': '游戏未在进行中'
        }), 400
    
    # 检查用户是否是游戏参与者
    if game.player1_id != current_user.id and game.player2_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': '无权在此游戏中落子'
        }), 403
    
    # 获取落子坐标
    data = request.get_json()
    x = data.get('x')
    y = data.get('y')
    
    if x is None or y is None:
        return jsonify({
            'status': 'error',
            'message': '缺少坐标'
        }), 400
    
    # 检查坐标是否有效
    if not (0 <= x < 15 and 0 <= y < 15):
        return jsonify({
            'status': 'error',
            'message': '坐标超出范围'
        }), 400
    
    # 检查是否轮到当前用户下棋
    moves_count = Move.query.filter_by(game_id=game_id).count()
    current_player_id = game.player1_id if moves_count % 2 == 0 else game.player2_id
    
    if current_user.id != current_player_id:
        return jsonify({
            'status': 'error',
            'message': '不是您的回合'
        }), 400
    
    # 检查该位置是否已有棋子
    existing_move = Move.query.filter_by(game_id=game_id, x=x, y=y).first()
    if existing_move:
        return jsonify({
            'status': 'error',
            'message': '该位置已有棋子'
        }), 400
    
    # 创建新的落子记录
    move = Move(
        game_id=game_id,
        player_id=current_user.id,
        x=x,
        y=y,
        move_number=moves_count + 1
    )
    
    db.session.add(move)
    db.session.flush()  # 刷新会话以获取 move.id
    
    # 检查是否获胜
    win = check_win(game_id, x, y, current_user.id)
    
    if win:
        # 更新游戏状态
        game.status = 'finished'
        game.end_time = datetime.utcnow()
        game.winner_id = current_user.id
        
        # 更新积分: 胜者+10，负者-10
        winner_id = current_user.id
        loser_id = game.player1_id if winner_id == game.player2_id else game.player2_id
        
        winner = User.query.get(winner_id)
        loser = User.query.get(loser_id)
        
        if winner and loser:
            winner.rating += 10
            loser.rating -= 10
            winner.wins += 1
            loser.losses += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'game_over': True,
            'winner_id': current_user.id,
            'points_change': 10 if current_user.id == winner_id else -10
        }), 200
    
    # 检查是否和棋（棋盘填满）
    if moves_count + 1 >= 15 * 15:
        game.status = 'finished'
        game.end_time = datetime.utcnow()
        
        # 和棋不改变积分
        player1 = User.query.get(game.player1_id)
        player2 = User.query.get(game.player2_id)
        
        if player1 and player2:
            player1.draws += 1
            player2.draws += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'game_over': True,
            'draw': True,
            'points_change': 0
        }), 200
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'move_id': move.id
    }), 201

@bp.route('/api/games/<int:game_id>/exit', methods=['POST'])
@login_required
def exit_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    # 检查用户是否是游戏参与者
    if game.player1_id != current_user.id and game.player2_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': '无权操作此游戏'
        }), 403
    
    # 只有游戏在等待中或进行中才能退出
    if game.status not in ['waiting', 'playing']:
        return jsonify({
            'status': 'error',
            'message': '游戏已结束，无法退出'
        }), 400
    
    # 暂存当前状态
    current_status = game.status
    
    # 更新游戏状态
    game.status = 'abandoned'
    game.end_time = datetime.utcnow()
    
    points_change = 0
    
    # 如果是对局中退出，另一方获胜
    if current_status == 'playing':
        if current_user.id == game.player1_id:
            game.winner_id = game.player2_id
            
            # 更新积分: 退出者-10，另一方+10
            player1 = User.query.get(game.player1_id)
            player2 = User.query.get(game.player2_id)
            
            if player1 and player2:
                player1.rating -= 10
                player2.rating += 10
                player1.losses += 1
                player2.wins += 1
                points_change = -10  # 当前退出玩家的积分变更
        else:
            game.winner_id = game.player1_id
            
            # 更新积分: 退出者-10，另一方+10
            player1 = User.query.get(game.player1_id)
            player2 = User.query.get(game.player2_id)
            
            if player1 and player2:
                player2.rating -= 10
                player1.rating += 10
                player2.losses += 1
                player1.wins += 1
                points_change = -10  # 当前退出玩家的积分变更
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'points_change': points_change
    }), 200

# 检查是否获胜
def check_win(game_id, x, y, player_id):
    # 获取该玩家在此游戏中的所有落子
    moves = Move.query.filter_by(game_id=game_id, player_id=player_id).all()
    
    # 将落子转换为坐标集合
    positions = set((move.x, move.y) for move in moves)
    
    # 检查水平方向
    count = 1
    # 向左检查
    for i in range(1, 5):
        if (x - i, y) in positions:
            count += 1
        else:
            break
    # 向右检查
    for i in range(1, 5):
        if (x + i, y) in positions:
            count += 1
        else:
            break
    if count >= 5:
        return True
    
    # 检查垂直方向
    count = 1
    # 向上检查
    for i in range(1, 5):
        if (x, y - i) in positions:
            count += 1
        else:
            break
    # 向下检查
    for i in range(1, 5):
        if (x, y + i) in positions:
            count += 1
        else:
            break
    if count >= 5:
        return True
    
    # 检查左上-右下对角线
    count = 1
    # 向左上检查
    for i in range(1, 5):
        if (x - i, y - i) in positions:
            count += 1
        else:
            break
    # 向右下检查
    for i in range(1, 5):
        if (x + i, y + i) in positions:
            count += 1
        else:
            break
    if count >= 5:
        return True
    
    # 检查右上-左下对角线
    count = 1
    # 向右上检查
    for i in range(1, 5):
        if (x + i, y - i) in positions:
            count += 1
        else:
            break
    # 向左下检查
    for i in range(1, 5):
        if (x - i, y + i) in positions:
            count += 1
        else:
            break
    if count >= 5:
        return True
    
    return False