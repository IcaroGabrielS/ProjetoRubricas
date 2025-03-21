from flask import Blueprint, request, jsonify
from models import db, Employee, Company, User
from middleware.auth import admin_required, user_has_company_access
from utils.validation import is_valid_uuid

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employees', methods=['GET'])
def list_employees():
    """Lista todos os funcionários que o usuário tem acesso"""
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Filtrar por empresa se especificado
    company_id = request.args.get('company_id')
    
    if user.is_admin:
        if company_id:
            if not is_valid_uuid(company_id):
                return jsonify({'message': 'ID de empresa inválido'}), 400
            employees = Employee.query.filter_by(company_id=company_id).all()
        else:
            employees = Employee.query.all()
    else:
        from models import CompanyPermission
        # Obter empresas que o usuário tem acesso
        permissions = CompanyPermission.query.filter_by(user_id=user_id).all()
        allowed_company_ids = [p.company_id for p in permissions]
        
        if company_id:
            if not is_valid_uuid(company_id):
                return jsonify({'message': 'ID de empresa inválido'}), 400
            if company_id not in allowed_company_ids:
                return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
            employees = Employee.query.filter_by(company_id=company_id).all()
        else:
            # Mostrar apenas funcionários de empresas que o usuário tem acesso
            employees = Employee.query.filter(Employee.company_id.in_(allowed_company_ids)).all()
    
    return jsonify({
        'employees': [emp.to_dict() for emp in employees]
    }), 200

@employees_bp.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Obtém detalhes de um funcionário específico"""
    employee = Employee.query.get_or_404(employee_id)
    
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Verificar se o usuário tem acesso à empresa do funcionário
    if employee.company_id and not user.is_admin:
        if not user_has_company_access(user_id, employee.company_id):
            return jsonify({'message': 'Acesso não autorizado a este funcionário'}), 403
    
    return jsonify({
        'employee': employee.to_dict()
    }), 200

@employees_bp.route('/employees', methods=['POST'])
@admin_required
def create_employee():
    """Cria um novo funcionário"""
    data = request.get_json()
    
    # Validar dados obrigatórios
    if not data or 'name' not in data or 'cpf' not in data:
        return jsonify({'message': 'Nome e CPF são obrigatórios'}), 400
    
    # Verificar se o CPF já existe
    existing = Employee.query.filter_by(cpf=data['cpf']).first()
    if existing:
        return jsonify({'message': 'CPF já cadastrado'}), 400
    
    # Criar funcionário
    new_employee = Employee(
        name=data['name'],
        cpf=data['cpf'],
        company_id=data.get('company_id'),
        i_empregados=data.get('i_empregados'),
        salario=data.get('salario'),
        admissao=data.get('admissao'),
        i_afastamentos=data.get('i_afastamentos')
    )
    
    db.session.add(new_employee)
    db.session.commit()
    
    return jsonify({
        'message': 'Funcionário cadastrado com sucesso',
        'employee': new_employee.to_dict()
    }), 201

@employees_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@admin_required
def update_employee(employee_id):
    """Atualiza um funcionário existente"""
    employee = Employee.query.get_or_404(employee_id)
    data = request.get_json()
    
    # Atualizar campos
    if 'name' in data:
        employee.name = data['name']
    if 'cpf' in data:
        # Verificar se o CPF já existe em outro funcionário
        existing = Employee.query.filter(Employee.cpf == data['cpf'], Employee.id != employee_id).first()
        if existing:
            return jsonify({'message': 'CPF já cadastrado para outro funcionário'}), 400
        employee.cpf = data['cpf']
    if 'company_id' in data:
        employee.company_id = data['company_id']
    if 'i_empregados' in data:
        employee.i_empregados = data['i_empregados']
    if 'salario' in data:
        employee.salario = data['salario']
    if 'admissao' in data:
        employee.admissao = data['admissao']
    if 'i_afastamentos' in data:
        employee.i_afastamentos = data['i_afastamentos']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Funcionário atualizado com sucesso',
        'employee': employee.to_dict()
    }), 200

@employees_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
@admin_required
def delete_employee(employee_id):
    """Remove um funcionário"""
    employee = Employee.query.get_or_404(employee_id)
    
    db.session.delete(employee)
    db.session.commit()
    
    return jsonify({
        'message': 'Funcionário removido com sucesso'
    }), 200