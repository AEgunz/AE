import os
from urllib.parse import quote_plus
from flask import Flask, send_from_directory
from dotenv import load_dotenv

from src.models import db
from src.routes.team import team_bp
from src.routes.match import match_bp
from src.routes.admin import admin_bp
from src.routes.ranking import ranking_bp
from src.routes.config import config_bp
from src.routes.register import register_bp

# تحميل متغيرات البيئة
load_dotenv()

# إنشاء تطبيق Flask (مرة واحدة فقط)
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# إعدادات التطبيق
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# إنشاء مجلدات التحميل إذا ما كانتش موجودة
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logos'), exist_ok=True)

# إعداد قاعدة البيانات
db_username = quote_plus(os.getenv('DB_USERNAME'))
db_password = quote_plus(os.getenv('DB_PASSWORD'))
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# تهيئة قاعدة البيانات مع التطبيق
db.init_app(app)
with app.app_context():
    db.create_all()

# تسجيل بلوبرينتس مع prefixes مناسبة
app.register_blueprint(register_bp, url_prefix='/api/register')
app.register_blueprint(team_bp, url_prefix='/api/teams')
app.register_blueprint(match_bp, url_prefix='/api/matches')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(ranking_bp, url_prefix='/api/rankings')
app.register_blueprint(config_bp, url_prefix='/api/config')

# راوت لاستضافة الملفات الستاتيكية و index.html fallback
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    full_path = os.path.join(static_folder_path, path)
    if path != "" and os.path.exists(full_path):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)