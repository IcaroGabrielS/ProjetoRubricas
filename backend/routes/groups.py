from flask import Blueprint, request, jsonify
from models import db, Group, GroupPermission, Company, User
from middleware.auth import admin_required, user_has_group_access
from utils.validation import is_valid_uuid

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/groups', methods=['POST'])
@admin_required
def create_group():
    data = request.get_json()
    user_id = request.headers.get('User-ID')
    
    new_group = Group(
        name=data['name'],
        created_by=user_id
    )
    
    db.session.add(new_group)
    db.session.commit()
    
    return jsonify({
        'message': 'Grupo criado com sucesso!',
        'group': new_group.to_dict()
    }), 201

@groups_bp.route('/groups', methods=['GET'])
def list_groups():
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    if user.is_admin:
        groups = Group.query.all()
        group_list = [group.to_dict_with_permissions() for group in groups]
    else:
        permissions = GroupPermission.query.filter_by(user_id=user_id).all()
        allowed_group_ids = [permission.group_id for permission in permissions]
        groups = Group.query.filter(Group.id.in_(allowed_group_ids)).all()
        group_list = [group.to_dict() for group in groups]
    
    return jsonify({
        'groups': group_list
    }), 200

@groups_bp.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
    
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    if not user.is_admin and not user_has_group_access(user_id, group_id):
        return jsonify({'message': 'Acesso não autorizado a este grupo'}), 403
    
    group = Group.query.get_or_404(group_id)
    
    if user.is_admin:
        group_dict = group.to_dict_with_permissions()
    else:
        group_dict = group.to_dict()
    
    companies = Company.query.filter_by(group_id=group_id).all()
    group_dict['companies'] = [company.to_dict() for company in companies]
    
    return jsonify({'group': group_dict}), 200

@groups_bp.route('/groups/<group_id>', methods=['DELETE'])
@admin_required
def delete_group(group_id):
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
        
    group = Group.query.get_or_404(group_id)
    
    GroupPermission.query.filter_by(group_id=group_id).delete()
    
    companies = Company.query.filter_by(group_id=group_id).all()
    for company in companies:
        # Cascade delete all related resources
        db.session.delete(company)
    
    db.session.delete(group)
    db.session.commit()
    
    return jsonify({'message': 'Grupo excluído com sucesso'}), 200

@groups_bp.route('/groups/<group_id>/permissions', methods=['GET', 'POST', 'DELETE'])
@admin_required
def manage_group_permissions(group_id):
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
        
    group = Group.query.get_or_404(group_id)
    
    if request.method == 'GET':
        permissions = GroupPermission.query.filter_by(group_id=group_id).all()
        users_with_access = []
        
        for permission in permissions:
            user = User.query.get(permission.user_id)
            if user:
                users_with_access.append(user.to_dict())
        
        return jsonify({
            'group_id': group_id,
            'users': users_with_access
        }), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'message': 'user_id é necessário'}), 400
        
        user_id = data['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        existing = GroupPermission.query.filter_by(group_id=group_id, user_id=user_id).first()
        if existing:
            return jsonify({'message': 'Usuário já tem acesso a este grupo'}), 400
        
        new_permission = GroupPermission(group_id=group_id, user_id=user_id)
        db.session.add(new_permission)
        db.session.commit()
        
        return jsonify({
            'message': 'Acesso concedido com sucesso',
            'permission': new_permission.to_dict()
        }), 201
    
    elif request.method == 'DELETE':
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'message': 'user_id é necessário'}), 400
        
        user_id = data['user_id']
        
        permission = GroupPermission.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not permission:
            return jsonify({'message': 'Usuário não tem acesso a este grupo'}), 404
        
        db.session.delete(permission)
        db.session.commit()
        
        return jsonify({
            'message': 'Acesso removido com sucesso'
        }), 200