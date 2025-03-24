from flask import request, jsonify, current_app
from functools import wraps
import jwt
from models import User, CompanyPermission

def get_token():
    """Extrai o token JWT do cabeçalho Authorization"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def get_current_user():
    """Extrai e valida o token JWT, retornando o usuário atual"""
    # Para compatibilidade com sistema antigo, verifica o header User-ID primeiro
    user_id = request.headers.get('User-ID')
    if user_id:
        return User.query.get(user_id)
        
    # Tenta o método JWT
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

def login_required(f):
    """Verifica se o usuário está autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({"message": "Authentication required"}), 401
            
        # Adiciona o usuário ao contexto da requisição para uso posterior
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Verifica se o usuário é um administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({"message": "Authentication required"}), 401
            
        if not user.is_admin:
            return jsonify({"message": "Access restricted to administrators"}), 403
            
        # Adiciona o usuário ao contexto da requisição para uso posterior
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def user_has_company_access(user_id, company_id):
    """Verifica se um usuário tem acesso a uma empresa específica"""
    # Checar se existe uma permissão de empresa para o usuário
    permission = CompanyPermission.query.filter_by(
        user_id=user_id,
        company_id=company_id
    ).first()
    
    return permission is not None