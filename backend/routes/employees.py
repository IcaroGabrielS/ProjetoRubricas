from flask import Blueprint, request, jsonify
from models import db, Employee, Company, User, CompanyPermission
from middleware.auth import admin_required, login_required, get_current_user, user_has_company_access
from utils.validation import is_valid_uuid

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employees', methods=['GET'])
@login_required
def list_employees():
    """Lista todos os funcionários que o usuário tem acesso"""
    user = get_current_user()
    
    # Implementação de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filtrar por empresa se especificado
    company_id = request.args.get('company_id')
    
    # Construir a query base
    query = Employee.query
    
    if user.is_admin:
        if company_id:
            if not is_valid_uuid(company_id):
                return jsonify({'message': 'ID de empresa inválido'}), 400
            query = query.filter_by(company_id=company_id)
    else:
        # Obter empresas que o usuário tem acesso
        permissions = CompanyPermission.query.filter_by(user_id=user.id).all()
        allowed_company_ids = [p.company_id for p in permissions]
        
        if company_id:
            if not is_valid_uuid(company_id):
                return jsonify({'message': 'ID de empresa inválido'}), 400
            if company_id not in allowed_company_ids:
                return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
            query = query.filter_by(company_id=company_id)
        else:
            # Mostrar apenas funcionários de empresas que o usuário tem acesso
            query = query.filter(Employee.company_id.in_(allowed_company_ids))
    
    # Adicionar ordenação
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')
    
    if hasattr(Employee, sort_by):
        if order == 'desc':
            query = query.order_by(getattr(Employee, sort_by).desc())
        else:
            query = query.order_by(getattr(Employee, sort_by).asc())
    
    # Filtro por nome (busca parcial)
    search = request.args.get('search')
    if search:
        query = query.filter(Employee.name.ilike(f'%{search}%'))
    
    # Executar a paginação
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'funcionarios': [emp.to_dict() for emp in pagination.items],
        'total': pagination.total,
        'paginas': pagination.pages,
        'pagina_atual': page
    }), 200

@employees_bp.route('/employees/<int:employee_id>', methods=['GET'])
@login_required
def get_employee(employee_id):
    """Obtém detalhes de um funcionário específico"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        user = get_current_user()
        
        # Verificar se o usuário tem acesso à empresa do funcionário
        if employee.company_id and not user.is_admin:
            if not user_has_company_access(user.id, employee.company_id):
                return jsonify({'message': 'Acesso não autorizado a este funcionário'}), 403
        
        return jsonify({
            'funcionario': employee.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar funcionário: {str(e)}'}), 500

@employees_bp.route('/employees', methods=['POST'])
@admin_required
def create_employee():
    """Cria um novo funcionário"""
    data = request.get_json() or {}
    
    # Validar dados obrigatórios
    if 'name' not in data or 'cpf' not in data:
        return jsonify({'message': 'Nome e CPF são obrigatórios'}), 400
    
    # Verificar se o CPF já existe
    existing = Employee.query.filter_by(cpf=data['cpf']).first()
    if existing:
        return jsonify({'message': 'CPF já cadastrado'}), 400
    
    try:
        # Criar funcionário
        new_employee = Employee(
            name=data['name'],
            cpf=data['cpf'],
            company_id=data.get('company_id'),
            i_empregados=data.get('i_empregados'),
            salario=data.get('salario'),
            admissao=data.get('admissao'),
            i_afastamentos=data.get('i_afastamentos'),
            codi_emp=data.get('codi_emp')
        )
        
        db.session.add(new_employee)
        db.session.commit()
        
        return jsonify({
            'message': 'Funcionário cadastrado com sucesso',
            'funcionario': new_employee.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao cadastrar funcionário: {str(e)}'}), 500

@employees_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@admin_required
def update_employee(employee_id):
    """Atualiza um funcionário existente"""
    data = request.get_json() or {}
    
    if not data:
        return jsonify({'message': 'Nenhum dado fornecido para atualização'}), 400
    
    try:
        employee = Employee.query.get_or_404(employee_id)
        
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
            if data['company_id'] is not None and not is_valid_uuid(data['company_id']):
                return jsonify({'message': 'ID de empresa inválido'}), 400
            employee.company_id = data['company_id']
        if 'i_empregados' in data:
            employee.i_empregados = data['i_empregados']
        if 'salario' in data:
            employee.salario = data['salario']
        if 'admissao' in data:
            employee.admissao = data['admissao']
        if 'i_afastamentos' in data:
            employee.i_afastamentos = data['i_afastamentos']
        if 'codi_emp' in data:
            employee.codi_emp = data['codi_emp']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Funcionário atualizado com sucesso',
            'funcionario': employee.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar funcionário: {str(e)}'}), 500

@employees_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
@admin_required
def delete_employee(employee_id):
    """Remove um funcionário"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'message': 'Funcionário removido com sucesso'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao remover funcionário: {str(e)}'}), 500