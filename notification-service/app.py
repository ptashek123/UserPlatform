from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt

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

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_token(token)
        
        if not user_data:
            return jsonify({'error': 'Unauthorized'}), 401

        # Stub: return mock notifications
        return jsonify({
            'notifications': [
                {'id': 1, 'message': 'Welcome to the platform!', 'read': False},
                {'id': 2, 'message': 'Your profile has been updated', 'read': True}
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')

        # Stub: log notification sending
        print(f"Sending notification to user {user_id}: {message}")
        
        return jsonify({'message': 'Notification sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003)

