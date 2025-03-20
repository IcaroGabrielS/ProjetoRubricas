from flask import Blueprint, request, jsonify
from models import db, Company, User, Employee, CompanyFile
from middleware.auth import admin_required, user_has_group_access
from utils.validation import is_valid_uuid

companies_bp = Blueprint('companies', __name__)

@companies_bp.route('/groups/<group_id>/companies', methods=['POST'])
@admin_required
def create_company(group_id):
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
        
    data = request.get_json()
    
    new_company = Company(
        name=data['name'],
        cnpj=data['cnpj'],
        group_id=group_id
    )
    
    db.session.add(new_company)
    db.session.commit()
    
    return jsonify({
        'message': 'Empresa criada com sucesso!',
        'company': new_company.to_dict()
    }), 201

@companies_bp.route('/groups/<group_id>/companies', methods=['GET'])
def list_companies(group_id):
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
        
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    if not user.is_admin and not user_has_group_access(user_id, group_id):
        return jsonify({'message': 'Acesso não autorizado a este grupo'}), 403
    
    companies = Company.query.filter_by(group_id=group_id).all()
    
    return jsonify({
        'companies': [company.to_dict() for company in companies]
    }), 200

@companies_bp.route('/companies/<company_id>', methods=['GET'])
def get_company(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    company = Company.query.get_or_404(company_id)
    
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
    
    files = CompanyFile.query.filter_by(company_id=company_id).all()
    employees = Employee.query.filter_by(company_id=company_id).all()
    
    company_dict = company.to_dict()
    company_dict['files'] = [file.to_dict() for file in files]
    company_dict['employees'] = [employee.to_dict() for employee in employees]
    
    return jsonify({'company': company_dict}), 200

@companies_bp.route('/companies/<company_id>', methods=['DELETE'])
@admin_required
def delete_company(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    company = Company.query.get_or_404(company_id)
    
    Employee.query.filter_by(company_id=company_id).delete()
    CompanyFile.query.filter_by(company_id=company_id).delete()
    
    db.session.delete(company)
    db.session.commit()
    
    return jsonify({'message': 'Empresa excluída com sucesso'}), 200