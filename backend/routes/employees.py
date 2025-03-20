from flask import Blueprint, request, jsonify
from models import db, Employee, Company, User
from middleware.auth import user_has_group_access
from utils.validation import is_valid_uuid

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/companies/<company_id>/employees', methods=['POST'])
def create_employee(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    company = Company.query.get_or_404(company_id)
    
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
    
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'message': 'Nome do funcionário é obrigatório'}), 400
    
    if not data.get('cpf'):
        return jsonify({'message': 'CPF do funcionário é obrigatório'}), 400
    
    existing_employee = Employee.query.filter_by(company_id=company_id, cpf=data['cpf']).first()
    if existing_employee:
        return jsonify({'message': 'Já existe um funcionário com este CPF nesta empresa'}), 400
    
    new_employee = Employee(
        name=data['name'],
        cpf=data['cpf'],
        company_id=company_id
    )
    
    db.session.add(new_employee)
    db.session.commit()
    
    return jsonify({
        'message': 'Funcionário criado com sucesso',
        'employee': new_employee.to_dict()
    }), 201

@employees_bp.route('/companies/<company_id>/employees', methods=['GET'])
def list_employees(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    company = Company.query.get_or_404(company_id)
    
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
    
    employees = Employee.query.filter_by(company_id=company_id).all()
    
    return jsonify({
        'employees': [employee.to_dict() for employee in employees]
    }), 200

@employees_bp.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    employee = Employee.query.get_or_404(employee_id)
    company = Company.query.get(employee.company_id)
    
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a este funcionário'}), 403
    
    return jsonify({
        'employee': employee.to_dict()
    }), 200

@employees_bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    employee = Employee.query.get_or_404(employee_id)
    company = Company.query.get(employee.company_id)
    
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a este funcionário'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        employee.name = data['name']
    
    if 'cpf' in data:
        existing_employee = Employee.query.filter_by(
            company_id=employee.company_id, 
            cpf=data['cpf']
        ).filter(Employee.id != employee_id).first()
        
        if existing_employee:
            return jsonify({'message': 'Já existe outro funcionário com este CPF nesta empresa'}), 400
        
        employee.cpf = data['cpf']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Funcionário atualizado com sucesso',
        'employee': employee.to_dict()
    }), 200

@employees_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    employee = Employee.query.get_or_404(employee_id)
    company = Company.query.get(employee.company_id)
    
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a este funcionário'}), 403
    
    db.session.delete(employee)
    db.session.commit()
    
    return jsonify({'message': 'Funcionário excluído com sucesso'}), 200