from flask import Blueprint, request, jsonify
from models import db, User, CompanyPermission, Company
from middleware.auth import admin_required, login_required, get_current_user

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
@admin_required
def register():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Nome de usuário e senha são obrigatórios'}), 400
    
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'Nome de usuário já existe'}), 400
    
    new_user = User(
        username=data['username'],
        password=data['password'],
        is_admin=data.get('is_admin', False)
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'Usuário registrado com sucesso', 'user': new_user.to_dict()}), 201

@users_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'user': user.to_dict()
    }), 200

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    
    if 'username' in data and data['username'] != user.username:
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'message': 'Nome de usuário já está em uso'}), 400
        user.username = data['username']
    
    if 'is_admin' in data:
        user.is_admin = data['is_admin']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Informações do usuário atualizadas com sucesso',
        'user': user.to_dict()
    }), 200

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    
    current_user = get_current_user()
    if current_user.id == user_id:
        return jsonify({'message': 'Não é possível excluir seu próprio usuário'}), 400
    
    companies_created = Company.query.filter_by(created_by=user_id).all()
    if companies_created:
        return jsonify({'message': 'Não é possível excluir este usuário porque ele criou empresas'}), 400
    
    CompanyPermission.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    return jsonify({'message': 'Usuário excluído com sucesso'}), 200

@users_bp.route('/users/<int:user_id>/change_password_no_verify', methods=['PUT'])
@login_required
def change_password_no_verify(user_id):
    data = request.get_json()
    current_user = get_current_user()
    
    user_to_change = User.query.get_or_404(user_id)
    
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    if 'new_password' not in data:
        return jsonify({'message': 'Nova senha é necessária'}), 400
    
    if len(data['new_password']) < 6:
        return jsonify({'message': 'A senha deve ter pelo menos 6 caracteres'}), 400
    
    user_to_change.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'}), 200

@users_bp.route('/users/<int:user_id>/password', methods=['PUT'])
@login_required
def change_password(user_id):
    data = request.get_json()
    current_user = get_current_user()
    
    user_to_change = User.query.get_or_404(user_id)
    
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    if 'new_password' not in data:
        return jsonify({'message': 'Nova senha é necessária'}), 400
    
    if len(data['new_password']) < 6:
        return jsonify({'message': 'A senha deve ter pelo menos 6 caracteres'}), 400
    
    if not current_user.is_admin and current_user.id == user_id:
        if 'current_password' not in data:
            return jsonify({'message': 'Senha atual é necessária'}), 400
        
        if not user_to_change.check_password(data['current_password']):
            return jsonify({'message': 'Senha atual incorreta'}), 400
    
    user_to_change.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'}), 200

@users_bp.route('/users/<int:user_id>/companies', methods=['GET'])
@admin_required
def get_user_companies(user_id):
    User.query.get_or_404(user_id)
    
    permissions = CompanyPermission.query.filter_by(user_id=user_id).all()
    company_ids = [permission.company_id for permission in permissions]
    
    from models import Company
    companies = Company.query.filter(Company.id.in_(company_ids)).all()
    
    return jsonify({
        'companies': [company.to_dict() for company in companies]
    }), 200