from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from ..models import User
import jwt
import datetime
import random
import string
import re

bp = Blueprint('auth', __name__)

# 存储验证码的字典
verification_codes = {}

def cleanup_expired_codes():
    """清理过期的验证码"""
    current_time = datetime.datetime.utcnow()
    expired_emails = [email for email, data in verification_codes.items() 
                     if current_time > data['expires']]
    for email in expired_emails:
        del verification_codes[email]

def is_valid_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

@bp.route('/api/auth/send-verification-code', methods=['POST'])
def send_verification_code():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': '邮箱不能为空'}), 400
    
    # 验证邮箱格式
    if not is_valid_email(email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 清理过期的验证码
    cleanup_expired_codes()
    
    # 发送验证码邮件
    try:
        sender_email = "3076688546@qq.com"
        sender_password = "opsznmfkafgudfeb"  # QQ邮箱授权码

        code, success = send_verification_email(email, sender_email, sender_password)

        if success:
            # 存储验证码到字典中，设置5分钟过期
            verification_codes[email] = {
                'code': code,
                'expires': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            }
            return jsonify({"message": "验证码已发送", "code": code}), 200
        else:
            return jsonify({"error": "验证码发送失败"}), 500
    except Exception as e:
        print(f'Failed to send email: {str(e)}')  # 添加错误日志
        return jsonify({'error': '发送验证码失败，请检查邮箱是否正确'}), 500



def generate_verification_code(length=6):
    """生成指定长度的随机验证码"""
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(email, sender_email, sender_password):
    """发送验证码到指定邮箱"""
    try:
        # 生成验证码
        code = generate_verification_code()
        
        # 邮件内容
        subject = "五子棋游戏注册验证码"
        body = f"您的验证码是：{code}，请在5分钟内使用。"
        
        # 创建邮件消息
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = formataddr(("五子棋游戏", sender_email))
        msg['To'] = email
        
        # 连接SMTP服务器
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender_email, sender_password)
        
        # 发送邮件
        server.sendmail(sender_email, [email], msg.as_string().encode('utf-8'))
        server.quit()
        
        return code, True
    except Exception as e:
        print(f"发送邮件失败: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印完整堆栈
        return None, False
    

@bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    verification_code = data.get('verificationCode')
    
    if not all([username, email, password, verification_code]):
        return jsonify({'error': '所有字段都是必填的'}), 400
    
    # 清理过期的验证码
    cleanup_expired_codes()
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被使用'}), 400
    
    # 验证验证码
    if email not in verification_codes:
        return jsonify({'error': '请先获取验证码'}), 400
    
    stored_code = verification_codes[email]
    if datetime.datetime.utcnow() > stored_code['expires']:
        del verification_codes[email]
        return jsonify({'error': '验证码已过期'}), 400
    
    if verification_code != stored_code['code']:
        return jsonify({'error': '验证码错误'}), 400
    
    # 验证通过，删除验证码
    del verification_codes[email]
    
    # 创建新用户
    user = User(username=username, email=email)
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
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=20)
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
        'created_at': current_user.created_at.strftime('%Y-%m-%d'),
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