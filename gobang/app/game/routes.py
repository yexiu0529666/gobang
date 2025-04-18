from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Game, Move, Match, User
from datetime import datetime, timedelta
from app.models import get_china_time

bp = Blueprint('game', __name__)

# 游戏最大不活跃时间（秒）
MAX_INACTIVITY_TIME = 1800  # 1800秒无操作自动判负

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

@bp.route('/api/games/<int:game_id>/heartbeat', methods=['POST'])
@login_required
def heartbeat(game_id):
    """
    心跳接口，更新玩家的最后活跃时间
    """
    user = current_user
    game = Game.query.get(game_id)
    
    if not game:
        return jsonify({'error': '游戏不存在'}), 404
    
    # 检查用户是否是游戏的参与者
    if game.player1_id != user.id and game.player2_id != user.id:
        return jsonify({'error': '您不是该游戏的参与者'}), 403
    
    # 更新玩家的最后活跃时间
    current_time = get_china_time()
    if game.player1_id == user.id:
        game.player1_last_active = current_time
    else:
        game.player2_last_active = current_time
    
    db.session.commit()
    
    return jsonify({'success': True})

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
    
    # 检查游戏是否正在进行中，并且检查玩家是否长时间未活动
    if game.status == 'playing':
        current_time = get_china_time()
        
        # 更新当前用户的活跃时间
        if current_user.id == game.player1_id:
            game.player1_last_active = current_time
        else:
            game.player2_last_active = current_time
        
        # 检查对手是否长时间未活动
        opponent_inactive = False
        inactive_player_id = None
        
        if current_user.id == game.player1_id and game.player2_last_active is not None:
            if (current_time - game.player2_last_active).total_seconds() > MAX_INACTIVITY_TIME:
                opponent_inactive = True
                inactive_player_id = game.player2_id
        elif current_user.id == game.player2_id and game.player1_last_active is not None:
            if (current_time - game.player1_last_active).total_seconds() > MAX_INACTIVITY_TIME:
                opponent_inactive = True
                inactive_player_id = game.player1_id
        
        # 如果对手长时间未活动，自动判负
        if opponent_inactive and inactive_player_id:
            # 更新游戏状态
            game.status = 'abandoned'
            game.end_time = current_time
            game.winner_id = current_user.id
            
            # 更新积分
            winner = User.query.get(current_user.id)
            loser = User.query.get(inactive_player_id)
            
            if winner and loser:
                winner.rating += 10
                loser.rating -= 10
                winner.wins += 1
                loser.losses += 1
                
                db.session.commit()
    
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

# 检查三三禁手
# 返回True表示违反三三禁手，False表示没有违反

def check_winning_move(x, y, positions, directions, board_size=15):
    """检查是否形成四子或五子连线"""
    for dx, dy in directions:
        count = 1
        for direction in [1, -1]:
            for i in range(1, 5):
                nx, ny = x + i * direction * dx, y + i * direction * dy
                if not (0 <= nx < board_size and 0 <= ny < board_size) or (nx, ny) not in positions:
                    break
                count += 1
        if count >= 4:
            print(f"发现四子或五子连线，方向: ({dx}, {dy}), 计数: {count}")
            return True
    return False

def find_active_threes(positions, all_positions, board_size=15):
    """查找棋盘上所有活三"""
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    active_threes = []
    
    # 遍历棋盘上所有可能的起点
    for x in range(board_size):
        for y in range(board_size):
            for dx, dy in directions:
                # 检查以 (x, y) 为起点的三连子
                three_line = [(x + i*dx, y + i*dy) for i in range(3)]
                
                # 边界检查
                if not all(0 <= px < board_size and 0 <= py < board_size for px, py in three_line):
                    continue
                
                # 检查是否为己方棋子
                if not all(pos in positions for pos in three_line):
                    continue
                
                # 检查两端是否为空
                left_point = (three_line[0][0] - dx, three_line[0][1] - dy)
                right_point = (three_line[2][0] + dx, three_line[2][1] + dy)
                
                left_open = (0 <= left_point[0] < board_size and 
                            0 <= left_point[1] < board_size and 
                            left_point not in all_positions)
                right_open = (0 <= right_point[0] < board_size and 
                             0 <= right_point[1] < board_size and 
                             right_point not in all_positions)
                
                if left_open and right_open:
                    active_threes.append(three_line)
    
    return active_threes

def check_three_three_rule(game_id, x, y, player_id, board_size=15):
    """
    检查是否违反三三禁手规则
    三三禁手：一子落下后，在棋盘上同时形成两个或以上的活三
    活三：在一条线上连续的三个己方棋子，且两端都有空位
    """
    print(f"检查三三禁手: 位置({x}, {y}), 玩家ID={player_id}")
    
    # 输入验证
    if not (0 <= x < board_size and 0 <= y < board_size):
        raise ValueError("落子位置超出棋盘范围")

    # 获取棋盘状态
    all_moves = Move.query.filter_by(game_id=game_id).all()
    if not all_moves:
        print("警告：未找到任何棋子记录")
    positions = set((move.x, move.y) for move in all_moves if move.player_id == player_id)
    all_positions = set((move.x, move.y) for move in all_moves)
    
    if (x, y) in all_positions:
        raise ValueError("当前位置已有棋子")
    
    print(f"玩家棋子（落子前）: {positions}")
    print(f"所有棋子（落子前）: {all_positions}")

    # 检查落子前的活三
    before_threes = find_active_threes(positions, all_positions, board_size)
    print(f"落子前的活三: {before_threes}")

    # 临时添加当前落子
    positions.add((x, y))
    all_positions.add((x, y))

    # 检查是否直接获胜
    if check_winning_move(x, y, positions, [(1, 0), (0, 1), (1, 1), (1, -1)], board_size):
        print("直接形成四子或五子连线，非禁手")
        return False

    # 检查落子后的活三
    after_threes = find_active_threes(positions, all_positions, board_size)
    print(f"落子后的活三: {after_threes}")

    # 找出新增的活三
    before_threes_set = {frozenset(three) for three in before_threes}
    new_threes = [three for three in after_threes if frozenset(three) not in before_threes_set]
    print(f"新增的活三: {new_threes}")

    # 判断三三禁手
    is_three_three = len(after_threes) >= 2
    print(f"三三禁手结果: {'违反' if is_three_three else '未违反'}")
    return is_three_three

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
    
    # 检查三三禁手，仅对黑子（假设为player1）适用
    if current_user.id == game.player1_id:
        print(f"\n========== 三三禁手检查开始 ==========")
        print(f"当前玩家是黑子 (ID={current_user.id}), 落子位置: ({x}, {y})")
        is_three_three = check_three_three_rule(game_id, x, y, current_user.id)
        print(f"三三禁手检查结果: {'违反三三禁手' if is_three_three else '未违反三三禁手'}")
        print(f"========== 三三禁手检查结束 ==========\n")
        
        if is_three_three:
            # 返回具体的错误信息，包括三三禁手的解释
            return jsonify({
                'status': 'error',
                'message': '违反三三禁手规则：黑棋不能在一步棋中同时形成两个或以上的活三'
            }), 400
    else:
        print(f"当前玩家是白子 (ID={current_user.id}), 跳过三三禁手检查")
    
    # 创建新的落子记录
    move = Move(
        game_id=game_id,
        player_id=current_user.id,
        x=x,
        y=y,
        move_number=moves_count + 1
    )
    
    db.session.add(move)
    db.session.flush()
    
    # 检查是否获胜
    win = check_win(game_id, x, y, current_user.id)
    
    if win:
        # 更新游戏状态
        game.status = 'finished'
        game.end_time = get_china_time()
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
        game.end_time = get_china_time()
        
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
    try:
        # 记录请求信息，帮助调试
        print(f"收到退出游戏请求: 用户ID={current_user.id}, 游戏ID={game_id}")
        
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
        
        # 记录游戏当前状态
        print(f"游戏状态变更: 从 {game.status} 到 abandoned")
        
        # 暂存当前状态
        current_status = game.status
        
        # 更新游戏状态
        game.status = 'abandoned'
        game.end_time = get_china_time()
        
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
                    print(f"更新积分: 玩家{player1.username}(-10), 玩家{player2.username}(+10)")
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
                    print(f"更新积分: 玩家{player2.username}(-10), 玩家{player1.username}(+10)")
        
        # 提交更改并确保成功
        try:
            db.session.commit()
            print(f"退出游戏成功完成: 游戏ID={game_id}")
        except Exception as e:
            db.session.rollback()
            print(f"退出游戏数据库错误: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '数据库更新失败'
            }), 500
        
        return jsonify({
            'status': 'success',
            'points_change': points_change
        }), 200
        
    except Exception as e:
        # 捕获所有未处理的异常
        print(f"退出游戏处理异常: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '服务器处理请求时出错'
        }), 500

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