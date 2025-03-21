from flask import Blueprint, request, jsonify
from models import db, Company, User, Employee, CompanyFile, CompanyPermission
from middleware.auth import admin_required, login_required, get_current_user, user_has_company_access
from utils.validation import is_valid_uuid

companies_bp = Blueprint('companies', __name__)

@companies_bp.route('/companies', methods=['POST'])
@admin_required
def create_company():
    data = request.get_json()
    user = get_current_user()
    
    # Validar dados obrigatórios
    if not data or 'name' not in data or 'cnpj' not in data:
        return jsonify({'message': 'Nome e CNPJ são obrigatórios'}), 400
    
    # Verificar se já existe empresa com este CNPJ
    existing = Company.query.filter_by(cnpj=data['cnpj']).first()
    if existing:
        return jsonify({'message': 'CNPJ já cadastrado'}), 400
    
    new_company = Company(
        name=data['name'],
        cnpj=data['cnpj'],
        created_by=user.id
    )
    
    db.session.add(new_company)
    db.session.commit()
    
    # Se forem especificados usuários com acesso, adicionar permissões
    if 'allowed_users' in data and isinstance(data['allowed_users'], list):
        for user_id in data['allowed_users']:
            user_exists = User.query.get(user_id)
            if user_exists:
                permission = CompanyPermission(
                    company_id=new_company.id,
                    user_id=user_id
                )
                db.session.add(permission)
        
        db.session.commit()
    
    return jsonify({
        'message': 'Empresa criada com sucesso!',
        'company': new_company.to_dict()
    }), 201

@companies_bp.route('/companies', methods=['GET'])
@login_required
def list_companies():
    user = get_current_user()
    
    if user.is_admin:
        companies = Company.query.all()
    else:
        # Buscar apenas empresas que o usuário tem acesso
        permissions = CompanyPermission.query.filter_by(user_id=user.id).all()
        company_ids = [p.company_id for p in permissions]
        companies = Company.query.filter(Company.id.in_(company_ids)).all()
    
    return jsonify({
        'companies': [company.to_dict() for company in companies]
    }), 200

@companies_bp.route('/companies/<company_id>', methods=['GET'])
@login_required
def get_company(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    user = get_current_user()
    company = Company.query.get_or_404(company_id)
    
    if not user.is_admin and not user_has_company_access(user.id, company_id):
        return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
    
    files = CompanyFile.query.filter_by(company_id=company_id).all()
    employees = Employee.query.filter_by(company_id=company_id).all()
    
    company_dict = company.to_dict()
    company_dict['files'] = [file.to_dict() for file in files]
    company_dict['employees'] = [employee.to_dict() for employee in employees]
    
    return jsonify({'company': company_dict}), 200

@companies_bp.route('/companies/<company_id>', methods=['PUT'])
@admin_required
def update_company(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    company = Company.query.get_or_404(company_id)
    data = request.get_json()
    
    if 'name' in data:
        company.name = data['name']
    
    if 'cnpj' in data and data['cnpj'] != company.cnpj:
        # Verificar se já existe outra empresa com este CNPJ
        existing = Company.query.filter(Company.cnpj == data['cnpj'], Company.id != company_id).first()
        if existing:
            return jsonify({'message': 'CNPJ já cadastrado para outra empresa'}), 400
        company.cnpj = data['cnpj']
    
    # Atualizar permissões de usuários se fornecidas
    if 'allowed_users' in data and isinstance(data['allowed_users'], list):
        # Remover permissões existentes
        CompanyPermission.query.filter_by(company_id=company_id).delete()
        
        # Adicionar novas permissões
        for user_id in data['allowed_users']:
            user_exists = User.query.get(user_id)
            if user_exists:
                permission = CompanyPermission(
                    company_id=company_id,
                    user_id=user_id
                )
                db.session.add(permission)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Empresa atualizada com sucesso',
        'company': company.to_dict_with_permissions()
    }), 200

@companies_bp.route('/companies/<company_id>', methods=['DELETE'])
@admin_required
def delete_company(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    company = Company.query.get_or_404(company_id)
    
    # Remover registros relacionados
    Employee.query.filter_by(company_id=company_id).update({Employee.company_id: None})
    CompanyFile.query.filter_by(company_id=company_id).delete()
    CompanyPermission.query.filter_by(company_id=company_id).delete()
    
    db.session.delete(company)
    db.session.commit()
    
    return jsonify({'message': 'Empresa excluída com sucesso'}), 200

@companies_bp.route('/companies/<company_id>/permissions', methods=['GET'])
@admin_required
def get_company_permissions(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    Company.query.get_or_404(company_id)
    
    permissions = CompanyPermission.query.filter_by(company_id=company_id).all()
    users_with_access = []
    
    for permission in permissions:
        user = User.query.get(permission.user_id)
        if user:
            users_with_access.append({
                'user_id': user.id,
                'username': user.username,
                'permission_id': permission.id,
                'created_at': permission.created_at.isoformat()
            })
    
    return jsonify({
        'company_id': company_id,
        'users_with_access': users_with_access
    }), 200