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

@app.route('/api/profile', methods=['GET'])
def get_profile():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_token(token)
        
        if not user_data:
            return jsonify({'error': 'Unauthorized'}), 401

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id, username, email, status, created_at FROM users WHERE id = %s",
            (user_data['user_id'],)
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'status': user['status'],
            'created_at': str(user['created_at'])
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_token(token)
        
        if not user_data:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()
        email = data.get('email')

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        if email:
            cursor.execute(
                "UPDATE users SET email = %s WHERE id = %s",
                (email, user_data['user_id'])
            )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002)

