from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    logo_path = db.Column(db.String(255), nullable=True)
    captain_name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(100), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_points = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer, nullable=True)
    
    # Relationships
    players = db.relationship('Player', backref='team', lazy=True, cascade="all, delete-orphan")
    match_results = db.relationship('MatchResult', backref='team', lazy=True)
    
    def __repr__(self):
        return f'<Team {self.name}>'

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    pubg_id = db.Column(db.String(100), nullable=True)  # Changed to nullable=True to make it optional
    
    def __repr__(self):
        return f'<Player {self.name}>'

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    map_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, live, completed, cancelled
    youtube_link = db.Column(db.String(255), nullable=True)
    
    # Relationships
    results = db.relationship('MatchResult', backref='match', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Match {self.name} on {self.match_date}>'

class MatchResult(db.Model):
    __tablename__ = 'match_results'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    position = db.Column(db.Integer, nullable=True)
    kills = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<MatchResult Match:{self.match_id} Team:{self.team_id}>'

class SiteConfig(db.Model):
    __tablename__ = 'site_config'
    id = db.Column(db.Integer, primary_key=True)
    site_title = db.Column(db.String(100), default='PUBG Mobile Tournament')
    donation_link = db.Column(db.String(255), default='https://streamlabs.com/aegaming91/tip')
    youtube_channel = db.Column(db.String(255), default='https://www.youtube.com/@Aegaming91')
    banner_image = db.Column(db.String(255), nullable=True)
    logo_image = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<SiteConfig {self.site_title}>'
