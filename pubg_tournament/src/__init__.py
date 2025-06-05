from flask import Flask
from src.models import db

def create_app():
    app = Flask(__name__)
    
    # تحميل الإعدادات
    app.config.from_pyfile('config.py')  # ولا استعمل config من env ولا حسب مشروعك
    
    # تهيئة قاعدة البيانات مع التطبيق
    db.init_app(app)
    
    # تسجيل البلوبريانتس
    from src.routes.team import team_bp
    from src.routes.match import match_bp
    from src.routes.admin import admin_bp
    from src.routes.ranking import ranking_bp
    from src.routes.config import config_bp
    from src.routes.register import register_bp

    app.register_blueprint(team_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ranking_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(register_bp)
    
    return app