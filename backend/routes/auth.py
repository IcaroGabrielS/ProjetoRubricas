from flask import Blueprint, request, jsonify, current_app
from models import db, User
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)

def get_token():
    """Extrai o token JWT do cabeçalho Authorization"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def get_user_from_token():
    """Extrai e valida o token JWT, retornando o usuário atual"""
    # Usando apenas o método JWT para autenticação
    token = get_token()
    if not token:
        return None
        
    try:
        payload = jwt.decode(
            token, 
            current_app.config['JWT_SECRET_KEY'],
            algorithms=["HS256"]
        )
        user_id = payload.get('sub')
        return User.query.get(user_id)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        token_payload = {
            'sub': user.id,
            'username': user.username,
            'is_admin': user.is_admin,
            'iss': 'projeto-rubricas',  # Issuer claim
            'iat': datetime.datetime.utcnow(),  # Issued at
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                seconds=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 24 * 60 * 60)
            )
        }
        token = jwt.encode(
            token_payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'is_admin': user.is_admin,
            'token': token
        }), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@auth_bp.route('/verify-token', methods=['GET'])
def verify_token():
    # Usar a função local para evitar importação circular
    user = get_user_from_token()
    if not user:
        return jsonify({'valid': False, 'message': 'Invalid or expired token'}), 401
        
    return jsonify({
        'valid': True,
        'user': user.to_dict()
    }), 200