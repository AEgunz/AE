import os
from flask import Blueprint, request, jsonify, current_app
from src.models import db, Match, MatchResult, Team

match_bp = Blueprint('match', __name__)

@match_bp.route('/', methods=['GET'])
def get_all_matches():
    matches = Match.query.all()
    result = []
    
    for match in matches:
        match_data = {
            'id': match.id,
            'name': match.name,
            'match_date': match.match_date,
            'map_name': match.map_name,
            'status': match.status,
            'youtube_link': match.youtube_link
        }
        result.append(match_data)
    
    return jsonify(result), 200

@match_bp.route('/<int:match_id>', methods=['GET'])
def get_match(match_id):
    match = Match.query.get_or_404(match_id)
    
    match_data = {
        'id': match.id,
        'name': match.name,
        'match_date': match.match_date,
        'map_name': match.map_name,
        'status': match.status,
        'youtube_link': match.youtube_link,
        'results': []
    }
    
    # Get match results with team information
    results = MatchResult.query.filter_by(match_id=match_id).all()
    for result in results:
        team = Team.query.get(result.team_id)
        result_data = {
            'team_id': result.team_id,
            'team_name': team.name if team else 'Unknown',
            'team_logo': team.logo_path if team else None,
            'position': result.position,
            'kills': result.kills,
            'points': result.points
        }
        match_data['results'].append(result_data)
    
    return jsonify(match_data), 200

@match_bp.route('/upcoming', methods=['GET'])
def get_upcoming_matches():
    from datetime import datetime
    
    upcoming_matches = Match.query.filter(
        Match.match_date >= datetime.utcnow(),
        Match.status == 'scheduled'
    ).order_by(Match.match_date).all()
    
    result = []
    for match in upcoming_matches:
        match_data = {
            'id': match.id,
            'name': match.name,
            'match_date': match.match_date,
            'map_name': match.map_name,
            'status': match.status,
            'youtube_link': match.youtube_link
        }
        result.append(match_data)
    
    return jsonify(result), 200

@match_bp.route('/live', methods=['GET'])
def get_live_matches():
    live_matches = Match.query.filter_by(status='live').all()
    
    result = []
    for match in live_matches:
        match_data = {
            'id': match.id,
            'name': match.name,
            'match_date': match.match_date,
            'map_name': match.map_name,
            'status': match.status,
            'youtube_link': match.youtube_link
        }
        result.append(match_data)
    
    return jsonify(result), 200
