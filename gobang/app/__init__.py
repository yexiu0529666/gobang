from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_cors import CORS
import eventlet
eventlet.monkey_patch()

db = SQLAlchemy()
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='eventlet',
    json={"dumps": str},
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gobang.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", json={"dumps": str})
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = None  # 禁用会话保护
    login_manager.unauthorized_handler = lambda: ('', 401)  # 未授权时返回 401 状态码

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 导入并注册蓝图
    from .auth.auth import bp as auth_bp
    from . import replay
    from .game.routes import bp as game_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(replay.bp)
    app.register_blueprint(game_bp)

    return app 