from flask import Blueprint, jsonify
import mysql.connector
import os

register_bp = Blueprint('register_bp', __name__)

@register_bp.route("/can_register")
def can_register():
    try:
        print("Trying to connect to DB...")
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        print("Connected.")
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        db.close()
        print(f"Count from DB: {count}")

        if count >= 25:
            return jsonify({"status": "closed", "message": "⛔ Registration Closed (25/25 teams)."}), 403
        else:
            return jsonify({"status": "open", "message": f"✅ {count}/25 teams registered — Registration Open."}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": f"❌ Error: {str(e)}"}), 500