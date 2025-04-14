from app import create_app, db
from app.models import User, Game, Move

app = create_app()

with app.app_context():
    # 创建所有表
    db.create_all()
    
    # 创建测试用户
    if not User.query.filter_by(username='test').first():
        test_user = User(username='test', email='test@example.com')
        test_user.set_password('test')
        db.session.add(test_user)
        db.session.commit()
        
    print('数据库初始化完成！') 