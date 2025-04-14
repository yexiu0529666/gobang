from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    games_as_player1 = db.relationship('Game', foreign_keys='Game.player1_id', backref='player1', lazy='dynamic')
    games_as_player2 = db.relationship('Game', foreign_keys='Game.player2_id', backref='player2', lazy='dynamic')
    games_won = db.relationship('Game', foreign_keys='Game.winner_id', backref='winner', lazy='dynamic')
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer, default=1000)  # 默认初始评分

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    moves = db.relationship('Move', backref='game', lazy='dynamic')
    status = db.Column(db.String(20), default='waiting')  # waiting, playing, finished, abandoned
    time_limit = db.Column(db.Integer, default=1800)  # 时间限制（秒）

class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    move_number = db.Column(db.Integer, nullable=False)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, closed

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 