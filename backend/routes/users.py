from flask import Blueprint, request, jsonify
from models import db, User, Group, GroupPermission
from middleware.auth import admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
@admin_required
def register():
    data = request.get_json()
    
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    new_user = User(
        username=data['username'],
        password=data['password'],
        is_admin=data.get('is_admin', False)
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'user': new_user.to_dict()}), 201

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
    
    admin_id = request.headers.get('User-ID')
    if int(admin_id) == user_id:
        return jsonify({'message': 'Não é possível excluir seu próprio usuário'}), 400
    
    groups_created = Group.query.filter_by(created_by=user_id).all()
    if groups_created:
        return jsonify({'message': 'Não é possível excluir este usuário porque ele criou grupos'}), 400
    
    GroupPermission.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    return jsonify({'message': 'Usuário excluído com sucesso'}), 200

@users_bp.route('/users/<int:user_id>/change_password_no_verify', methods=['PUT'])
def change_password_no_verify(user_id):
    data = request.get_json()
    current_user_id = request.headers.get('User-ID')
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    user_to_change = User.query.get_or_404(user_id)
    
    if not current_user.is_admin and int(current_user_id) != user_id:
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    if 'new_password' not in data:
        return jsonify({'message': 'Nova senha é necessária'}), 400
    
    if len(data['new_password']) < 6:
        return jsonify({'message': 'A senha deve ter pelo menos 6 caracteres'}), 400
    
    user_to_change.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'}), 200

@users_bp.route('/users/<int:user_id>/password', methods=['PUT'])
def change_password(user_id):
    data = request.get_json()
    current_user_id = request.headers.get('User-ID')
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    user_to_change = User.query.get_or_404(user_id)
    
    if not current_user.is_admin and int(current_user_id) != user_id:
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    if 'new_password' not in data:
        return jsonify({'message': 'Nova senha é necessária'}), 400
    
    if len(data['new_password']) < 6:
        return jsonify({'message': 'A senha deve ter pelo menos 6 caracteres'}), 400
    
    if not current_user.is_admin and int(current_user_id) == user_id:
        if 'current_password' not in data:
            return jsonify({'message': 'Senha atual é necessária'}), 400
        
        if not user_to_change.check_password(data['current_password']):
            return jsonify({'message': 'Senha atual incorreta'}), 400
    
    user_to_change.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'}), 200

@users_bp.route('/users/<int:user_id>/groups', methods=['GET'])
@admin_required
def get_user_groups(user_id):
    User.query.get_or_404(user_id)
    
    permissions = GroupPermission.query.filter_by(user_id=user_id).all()
    group_ids = [permission.group_id for permission in permissions]
    
    groups = Group.query.filter(Group.id.in_(group_ids)).all()
    
    return jsonify({
        'groups': [group.to_dict() for group in groups]
    }), 200