from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from .. import db
from ..models import User
import jwt
import datetime

bp = Blueprint('auth', __name__)

@bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')  # 邮箱现在是可选的
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    # 创建新用户
    user = User(username=username)
    if email:  # 如果提供了邮箱，则设置
        user.email = email
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '注册成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 201

@bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    login_user(user)
    
    # 生成 JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, 'secret-key', algorithm='HS256')
    
    return jsonify({
        'message': 'Logged in successfully',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })

@bp.route('/api/auth/logout', methods=['POST'])
def logout():
    if not current_user.is_authenticated:
        return jsonify({'error': '未登录'}), 401
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/api/auth/me')
@login_required
def get_profile():
    # 计算总场次（作为玩家1和玩家2的场次之和）
    games_as_p1 = current_user.games_as_player1.all()
    games_as_p2 = current_user.games_as_player2.all()
    total_games = len(games_as_p1) + len(games_as_p2)
    
    # 计算胜场数（作为玩家1和玩家2的胜场之和）
    games_won = sum(1 for game in games_as_p1 if game.winner_id == current_user.id) + \
                sum(1 for game in games_as_p2 if game.winner_id == current_user.id)
    
    # 计算负场数（总场次减去胜场数）
    games_lost = total_games - games_won
    
    # 计算胜率
    win_rate = (games_won / total_games * 100) if total_games > 0 else 0
    
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'total_games': total_games,
        'games_won': games_won,
        'games_lost': games_lost,
        'win_rate': round(win_rate, 2),  # 保留两位小数
        'rating': current_user.rating  # 添加积分信息
    })

@bp.route('/api/me', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    
    if 'email' in data:
        current_user.email = data['email']
    
    if 'password' in data:
        current_user.set_password(data['password'])
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}) 