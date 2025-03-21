from flask import Blueprint, request, jsonify, current_app
from models import db, User
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    # Melhoria: Adicionar validação para garantir que username e password existam
    data = request.get_json() or {}
    
    if 'username' not in data or 'password' not in data:
        return jsonify({'mensagem': 'Nome de usuário e senha são obrigatórios'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        # Criação do token JWT
        token_payload = {
            'sub': user.id,
            'username': user.username,
            'is_admin': user.is_admin,
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
            'mensagem': 'Login realizado com sucesso',
            'user_id': user.id,
            'username': user.username,
            'is_admin': user.is_admin,
            'token': token
        }), 200
    
    return jsonify({'mensagem': 'Nome de usuário ou senha inválidos'}), 401

@auth_bp.route('/verify-token', methods=['GET'])
def verify_token():
    from middleware.auth import get_current_user
    
    user = get_current_user()
    if not user:
        return jsonify({'valid': False, 'mensagem': 'Token inválido ou expirado'}), 401
        
    return jsonify({
        'valid': True,
        'user': user.to_dict()
    }), 200