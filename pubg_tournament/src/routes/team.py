import io
import os
import uuid
import pandas as pd
import requests
from flask import Blueprint, request, jsonify, current_app
from flask import Blueprint, send_file, current_app
from werkzeug.utils import secure_filename
from src.models import db, Team, Player
from flask import send_file
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from tempfile import NamedTemporaryFile
from src.models import Team
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenPyxlImage
from src import db

team_bp = Blueprint('team', __name__)

if __name__ == '__main__':
    app.run(debug=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@team_bp.route('/register', methods=['POST'])
def register_team():
    if 'logo' not in request.files:
        return jsonify({'error': 'No logo file provided'}), 400
    
    logo_file = request.files['logo']
    
    if logo_file.filename == '':
        return jsonify({'error': 'No logo file selected'}), 400
    
    if not allowed_file(logo_file.filename):
        return jsonify({'error': 'File type not allowed. Please upload PNG, JPG, JPEG, or GIF'}), 400

        # Check if registration is closed
    count = Team.query.count()
    print(f"عدد الفرق المسجلة دابا: {count}")
    if count >= 25:
        return jsonify({
            'error': '⛔ التسجيل تسد! وصلنا 25 فريق.'
    }), 403
    
    if 'logo' not in request.files:
        return jsonify({'error': 'No logo file provided'}), 400
    
    logo_file = request.files['logo']
    
    if logo_file.filename == '':
        return jsonify({'error': 'No logo file selected'}), 400
    
    if not allowed_file(logo_file.filename):
        return jsonify({'error': 'File type not allowed. Please upload PNG, JPG, JPEG, or GIF'}), 400
    
    data = request.form
    team_name = data.get('name')
    captain_name = data.get('captain_name')
    contact_info = data.get('contact_info')
    
    if not team_name or not captain_name or not contact_info:
        return jsonify({'error': 'Missing required fields'}), 400
    
    existing_team = Team.query.filter_by(name=team_name).first()
    if existing_team:
        return jsonify({'error': 'سمية الفريق راه موجودة من قبل ⚠️'}), 400
    
    filename = secure_filename(logo_file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    logo_path = os.path.join('uploads', 'logos', unique_filename)
    full_path = os.path.join(current_app.static_folder, 'uploads', 'logos', unique_filename)
    logo_file.save(full_path)
    
    new_team = Team(
        name=team_name,
        logo_path=logo_path,
        captain_name=captain_name,
        contact_info=contact_info
    )
    
    players_data = request.form.getlist('players')
    
    try:
        db.session.add(new_team)
        db.session.flush()
        
        for player_name in players_data:
            if player_name:
                player = Player(
                    team_id=new_team.id,
                    name=player_name,
                    pubg_id=None
                )
                db.session.add(player)
        
        db.session.commit()
        return jsonify({
            'message': 'الفريق تسجل بنجاح ✅',
            'team_id': new_team.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500    
    
    # Get form data
    data = request.form
    team_name = data.get('name')
    captain_name = data.get('captain_name')
    contact_info = data.get('contact_info')
    
    # Validate required fields
    if not team_name or not captain_name or not contact_info:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if team name already exists
    existing_team = Team.query.filter_by(name=team_name).first()
    if existing_team:
        return jsonify({'error': 'Team name already exists'}), 400
    
    # Save logo file with unique name
    filename = secure_filename(logo_file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    logo_path = os.path.join('uploads', 'logos', unique_filename)
    full_path = os.path.join(current_app.static_folder, 'uploads', 'logos', unique_filename)
    logo_file.save(full_path)
    
    # Create new team
    new_team = Team(
        name=team_name,
        logo_path=logo_path,
        captain_name=captain_name,
        contact_info=contact_info
    )
    
    # Add players if provided
    players_data = request.form.getlist('players')
    
    try:
        db.session.add(new_team)
        db.session.flush()  # Get the team ID without committing
        
        # Add players
        for player_name in players_data:
            if player_name:
                player = Player(
                    team_id=new_team.id,
                    name=player_name,
                    pubg_id=None  # No longer required
                )
                db.session.add(player)
        
        db.session.commit()
        return jsonify({
            'message': 'الفريق تسجل بنجاح ✅',
            'team_id': new_team.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@team_bp.route('/', methods=['GET'])
def get_all_teams():
    teams = Team.query.all()
    result = []
    
    for team in teams:
        team_data = {
            'id': team.id,
            'name': team.name,
            'logo_path': team.logo_path,
            'captain_name': team.captain_name,
            'registration_date': team.registration_date,
            'total_points': team.total_points,
            'rank': team.rank,
            'players': []
        }
        
        for player in team.players:
            team_data['players'].append({
                'id': player.id,
                'name': player.name,
                'pubg_id': player.pubg_id
            })
        
        result.append(team_data)
    
    return jsonify(result), 200

@team_bp.route('/<int:team_id>', methods=['GET'])
def get_team(team_id):
    team = Team.query.get_or_404(team_id)
    
    team_data = {
        'id': team.id,
        'name': team.name,
        'logo_path': team.logo_path,
        'captain_name': team.captain_name,
        'contact_info': team.contact_info,
        'registration_date': team.registration_date,
        'total_points': team.total_points,
        'rank': team.rank,
        'players': []
    }
    
    for player in team.players:
        team_data['players'].append({
            'id': player.id,
            'name': player.name,
            'pubg_id': player.pubg_id
        })
    
    return jsonify(team_data), 200
      
@team_bp.route('/export')
def export_teams_excel():
    teams = Team.query.all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Teams"

    # Header row
    headers = ["ID", "Name", "Captain", "Registration Date", "Points", "Logo"]
    ws.append(headers)

    for idx, t in enumerate(teams, start=2):
        # Append data (image will be added separately)
        ws.append([
            t.id,
            t.name,
            t.captain_name,
            t.registration_date.strftime('%Y-%m-%d'),
            t.total_points,
            ""  # placeholder for image
        ])

        if t.logo_path:
            full_path = os.path.join(current_app.root_path, t.logo_path)
            print("LOGO PATH:", t.logo_path)
            print("FULL PATH:", full_path)
            print("EXISTS:", os.path.exists(full_path))

        if t.logo_path:
            # مسار كامل للصورة فالسيرفر
            full_path = os.path.join(current_app.root_path, 'static', t.logo_path)

            # تأكد الصورة موجودة
            if os.path.exists(full_path):
                try:
                    img = OpenPyxlImage(full_path)
                    img.width = 40
                    img.height = 40
                    ws.add_image(img, f"F{idx}")  # F = logo column
                except Exception as e:
                    print(f"خطأ في تحميل الصورة: {e}")

    # Create the Excel file in memory
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='teams_with_logos.xlsx'
    )


