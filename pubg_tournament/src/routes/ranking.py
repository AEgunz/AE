from flask import Blueprint, jsonify
from src.models import Team

ranking_bp = Blueprint('ranking', __name__)

@ranking_bp.route('/', methods=['GET'])
def get_team_rankings():
    """Get all teams sorted by points in descending order"""
    teams = Team.query.order_by(Team.total_points.desc()).all()
    result = []
    
    for team in teams:
        team_data = {
            'id': team.id,
            'name': team.name,
            'logo_path': team.logo_path,
            'rank': team.rank,
            'total_points': team.total_points
        }
        result.append(team_data)
    
    return jsonify(result), 200

@ranking_bp.route('/top/<int:limit>', methods=['GET'])
def get_top_teams(limit):
    """Get top N teams by points"""
    if limit <= 0:
        return jsonify({'error': 'Limit must be greater than 0'}), 400
        
    teams = Team.query.order_by(Team.total_points.desc()).limit(limit).all()
    result = []
    
    for team in teams:
        team_data = {
            'id': team.id,
            'name': team.name,
            'logo_path': team.logo_path,
            'rank': team.rank,
            'total_points': team.total_points
        }
        result.append(team_data)
    
    return jsonify(result), 200
