import os
from flask import Blueprint, request, jsonify, current_app
from src.models import db, User, Team, Player, Match, MatchResult, SiteConfig

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=username, is_admin=True).first()
    
    if not user or user.password != password:  # In production, use proper password hashing
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user_id': user.id,
        'username': user.username,
        'is_admin': user.is_admin
    }), 200

@admin_bp.route('/matches', methods=['POST'])
def create_match():
    data = request.json
    
    if not data.get('name') or not data.get('match_date') or not data.get('map_name'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_match = Match(
        name=data.get('name'),
        match_date=data.get('match_date'),
        map_name=data.get('map_name'),
        status=data.get('status', 'scheduled'),
        youtube_link=data.get('youtube_link')
    )
    
    try:
        db.session.add(new_match)
        db.session.commit()
        return jsonify({
            'message': 'Match created successfully',
            'match_id': new_match.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/matches/<int:match_id>', methods=['PUT'])
def update_match(match_id):
    match = Match.query.get_or_404(match_id)
    data = request.json
    
    if 'name' in data:
        match.name = data['name']
    if 'match_date' in data:
        match.match_date = data['match_date']
    if 'map_name' in data:
        match.map_name = data['map_name']
    if 'status' in data:
        match.status = data['status']
    if 'youtube_link' in data:
        match.youtube_link = data['youtube_link']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Match updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/results', methods=['POST'])
def add_match_result():
    data = request.json
    
    if not data.get('match_id') or not data.get('team_id'):
        return jsonify({'error': 'Match ID and Team ID are required'}), 400
    
    # Check if result already exists
    existing_result = MatchResult.query.filter_by(
        match_id=data.get('match_id'),
        team_id=data.get('team_id')
    ).first()
    
    if existing_result:
        return jsonify({'error': 'Result already exists for this team in this match'}), 400
    
    new_result = MatchResult(
        match_id=data.get('match_id'),
        team_id=data.get('team_id'),
        position=data.get('position'),
        kills=data.get('kills', 0),
        points=data.get('points', 0)
    )
    
    try:
        db.session.add(new_result)
        db.session.commit()
        
        # Update team total points
        update_team_points(data.get('team_id'))
        
        return jsonify({
            'message': 'Match result added successfully',
            'result_id': new_result.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/results/<int:result_id>', methods=['PUT'])
def update_match_result(result_id):
    result = MatchResult.query.get_or_404(result_id)
    data = request.json
    
    if 'position' in data:
        result.position = data['position']
    if 'kills' in data:
        result.kills = data['kills']
    if 'points' in data:
        result.points = data['points']
    
    try:
        db.session.commit()
        
        # Update team total points
        update_team_points(result.team_id)
        
        return jsonify({'message': 'Match result updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/config', methods=['GET', 'PUT'])
def manage_site_config():
    config = SiteConfig.query.first()
    
    if not config:
        config = SiteConfig()
        db.session.add(config)
        db.session.commit()
    
    if request.method == 'GET':
        return jsonify({
            'site_title': config.site_title,
            'donation_link': config.donation_link,
            'youtube_channel': config.youtube_channel,
            'banner_image': config.banner_image,
            'logo_image': config.logo_image
        }), 200
    
    elif request.method == 'PUT':
        data = request.json
        
        if 'site_title' in data:
            config.site_title = data['site_title']
        if 'donation_link' in data:
            config.donation_link = data['donation_link']
        if 'youtube_channel' in data:
            config.youtube_channel = data['youtube_channel']
        if 'banner_image' in data:
            config.banner_image = data['banner_image']
        if 'logo_image' in data:
            config.logo_image = data['logo_image']
        
        try:
            db.session.commit()
            return jsonify({'message': 'Site configuration updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

def update_team_points(team_id):
    """Update team's total points based on all match results"""
    team = Team.query.get(team_id)
    if not team:
        return
    
    # Calculate total points from all matches
    results = MatchResult.query.filter_by(team_id=team_id).all()
    total_points = sum(result.points for result in results)
    
    team.total_points = total_points
    db.session.commit()
    
    # Update rankings for all teams
    update_rankings()

def update_rankings():
    """Update rankings for all teams based on total points"""
    teams = Team.query.order_by(Team.total_points.desc()).all()
    
    for i, team in enumerate(teams):
        team.rank = i + 1
    
    db.session.commit()

@admin_bp.route('/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    
    try:
        # Delete associated match results first
        MatchResult.query.filter_by(match_id=match_id).delete()
        
        # Then delete the match
        db.session.delete(match)
        db.session.commit()
        return jsonify({'message': 'Match deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    team = Team.query.get_or_404(team_id)
    data = request.json
    
    if 'name' in data:
        team.name = data['name']
    if 'captain_name' in data:
        team.captain_name = data['captain_name']
    if 'contact_info' in data:
        team.contact_info = data['contact_info']
    if 'total_points' in data:
        team.total_points = data['total_points']
        
    try:
        db.session.commit()
        
        # Update rankings after team points change
        update_rankings()
        
        return jsonify({'message': 'Team updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/teams/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    
    try:
        # Delete associated match results first
        MatchResult.query.filter_by(team_id=team_id).delete()
        
        # Delete associated players
        Player.query.filter_by(team_id=team_id).delete()
        
        # Then delete the team
        db.session.delete(team)
        db.session.commit()
        
        # Update rankings after team deletion
        update_rankings()
        
        return jsonify({'message': 'Team deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/results/<int:result_id>', methods=['DELETE'])
def delete_match_result(result_id):
    result = MatchResult.query.get_or_404(result_id)
    team_id = result.team_id
    
    try:
        db.session.delete(result)
        db.session.commit()
        
        # Update team points and rankings
        update_team_points(team_id)
        
        return jsonify({'message': 'Match result deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
