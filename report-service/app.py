from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'postgres-service')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'userplatform')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# JWT Secret
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def verify_token(token):
    try:
        if not token:
            return None
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return decoded
    except:
        return None

@app.route('/health/live', methods=['GET'])
def liveness():
    return jsonify({'status': 'alive'}), 200

@app.route('/health/ready', methods=['GET'])
def readiness():
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'status': 'ready'}), 200
    return jsonify({'status': 'not ready'}), 503

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_token(token)
        
        if not user_data:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()
        report_type = data.get('type', 'user_stats')

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Generate mock report
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as active FROM users WHERE status = 'active'")
        active_users = cursor.fetchone()['active']
        
        conn.close()

        report = {
            'type': report_type,
            'generated_at': datetime.now().isoformat(),
            'statistics': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users
            }
        }

        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/list', methods=['GET'])
def list_reports():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_token(token)
        
        if not user_data:
            return jsonify({'error': 'Unauthorized'}), 401

        # Stub: return mock reports list
        return jsonify({
            'reports': [
                {'id': 1, 'type': 'daily_stats', 'created_at': '2024-01-01'},
                {'id': 2, 'type': 'user_activity', 'created_at': '2024-01-02'}
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004)

