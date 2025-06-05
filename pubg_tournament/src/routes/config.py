from flask import Blueprint, jsonify
from src.models import SiteConfig

config_bp = Blueprint('config', __name__)

@config_bp.route('/', methods=['GET'])
def get_site_config():
    """Get site configuration including donation and YouTube links"""
    config = SiteConfig.query.first()
    
    if not config:
        config = SiteConfig()  # Create default config if none exists
    
    return jsonify({
        'site_title': config.site_title,
        'donation_link': config.donation_link,
        'youtube_channel': config.youtube_channel,
        'banner_image': config.banner_image,
        'logo_image': config.logo_image
    }), 200
