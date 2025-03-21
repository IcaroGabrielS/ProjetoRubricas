from flask import Blueprint, request, jsonify, current_app
from models import db, Employee, Company, CompanyPermission
from middleware.auth import admin_required, get_current_user
import pyodbc

imports_bp = Blueprint('imports', __name__)

@imports_bp.route('/import/employees', methods=['POST'])
@admin_required
def import_employees():
    try:
        # Parâmetros de conexão - podem ser passados no request ou usar os padrões
        data = request.get_json() or {}
        conn_params = {
            "Driver": data.get("Driver", "{SQL Anywhere 17}"),
            "Host": data.get("Host", "10.0.25.19"),
            "Server": data.get("Server", "Srvcontabil"),
            "DatabaseName": data.get("DatabaseName", "Contabil"),
            "UID": data.get("UID", "externo"),
            "PWD": data.get("PWD", "externo"),
            "Port": data.get("Port", "2638")
        }
        
        # Estabelecer conexão
        conn_str = ";".join([f"{k}={v}" for k, v in conn_params.items()])
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Executar a consulta com a coluna codi_emp
        query = "SELECT i_empregados, nome, salario, cpf, admissao, I_AFASTAMENTOS, codi_emp FROM bethadba.foempregados"
        cursor.execute(query)
        
        # Processar resultados
        employees_added = 0
        employees_updated = 0
        errors = []
        
        for row in cursor.fetchall():
            try:
                i_empregados, nome, salario, cpf, admissao, i_afastamentos, codi_emp = row
                
                # Formatar CPF - remover pontos e traços
                cpf = ''.join(filter(str.isdigit, cpf if cpf else ""))
                
                # Verificar se o funcionário já existe
                existing_employee = Employee.query.filter_by(i_empregados=i_empregados).first()
                
                if existing_employee:
                    # Atualizar funcionário existente
                    existing_employee.name = nome
                    existing_employee.salario = salario
                    existing_employee.cpf = cpf
                    existing_employee.admissao = admissao
                    existing_employee.i_afastamentos = i_afastamentos
                    existing_employee.codi_emp = codi_emp
                    employees_updated += 1
                else:
                    # Criar novo funcionário
                    new_employee = Employee(
                        i_empregados=i_empregados,
                        name=nome,
                        salario=salario,
                        cpf=cpf,
                        admissao=admissao,
                        i_afastamentos=i_afastamentos,
                        codi_emp=codi_emp
                    )
                    db.session.add(new_employee)
                    employees_added += 1
                
                # Commit a cada 100 registros para evitar problemas de memória
                if (employees_added + employees_updated) % 100 == 0:
                    db.session.commit()
            
            except Exception as e:
                errors.append(f"Erro ao processar funcionário {row[0] if row else 'desconhecido'}: {str(e)}")
        
        # Commit final
        db.session.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Importação concluída",
            "employees_added": employees_added,
            "employees_updated": employees_updated,
            "errors": errors
        }), 200
        
    except pyodbc.Error as e:
        return jsonify({
            "message": f"Erro de conexão ODBC: {str(e)}",
            "success": False
        }), 500
    except Exception as e:
        return jsonify({
            "message": f"Erro: {str(e)}",
            "success": False
        }), 500

@imports_bp.route('/employees/unassigned', methods=['GET'])
@admin_required
def get_unassigned_employees():
    """Retorna todos os funcionários que não estão associados a nenhuma empresa"""
    unassigned = Employee.query.filter_by(company_id=None).all()
    return jsonify({
        "count": len(unassigned),
        "employees": [emp.to_dict() for emp in unassigned]
    }), 200

@imports_bp.route('/employees/assign', methods=['POST'])
@admin_required
def assign_employees():
    """Associa funcionários a uma empresa manualmente por IDs"""
    data = request.get_json()
    
    if not data or 'company_id' not in data or 'employee_ids' not in data:
        return jsonify({"message": "company_id e employee_ids são necessários"}), 400
    
    company_id = data['company_id']
    employee_ids = data['employee_ids']
    
    if not isinstance(employee_ids, list):
        return jsonify({"message": "employee_ids deve ser uma lista"}), 400
    
    count = 0
    errors = []
    
    for emp_id in employee_ids:
        try:
            employee = Employee.query.get(emp_id)
            if employee:
                employee.company_id = company_id
                count += 1
            else:
                errors.append(f"Funcionário ID {emp_id} não encontrado")
        except Exception as e:
            errors.append(f"Erro ao associar funcionário ID {emp_id}: {str(e)}")
    
    db.session.commit()
    
    return jsonify({
        "message": f"{count} funcionários associados à empresa com sucesso",
        "errors": errors
    }), 200

@imports_bp.route('/employees/codes', methods=['GET'])
@admin_required
def list_employee_codes():
    """Lista todos os códigos de empresa (codi_emp) distintos dos funcionários sem associação"""
    
    # Query para obter códigos únicos de funcionários sem empresa associada
    codes = db.session.query(Employee.codi_emp, db.func.count(Employee.id).label('count'))\
        .filter(Employee.company_id.is_(None))\
        .group_by(Employee.codi_emp)\
        .all()
    
    result = {
        "total_unassigned": sum(count for _, count in codes),
        "codes": [{"code": code, "count": count} for code, count in codes if code]
    }
    
    return jsonify(result), 200

@imports_bp.route('/import/companies', methods=['POST'])
@admin_required
def import_companies():
    try:
        # Parâmetros de conexão - podem ser passados no request ou usar os padrões
        data = request.get_json() or {}
        conn_params = {
            "Driver": data.get("Driver", "{SQL Anywhere 17}"),
            "Host": data.get("Host", "10.0.25.19"),
            "Server": data.get("Server", "Srvcontabil"),
            "DatabaseName": data.get("DatabaseName", "Contabil"),
            "UID": data.get("UID", "externo"),
            "PWD": data.get("PWD", "externo"),
            "Port": data.get("Port", "2638")
        }
        
        # Estabelecer conexão
        conn_str = ";".join([f"{k}={v}" for k, v in conn_params.items()])
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Executar a consulta para importar empresas
        query = "SELECT cgce_emp, apel_emp, codi_emp FROM bethadba.geempre"
        cursor.execute(query)
        
        # Processar resultados
        companies_added = 0
        companies_updated = 0
        errors = []
        
        for row in cursor.fetchall():
            try:
                cgce_emp, apel_emp, codi_emp = row
                
                # Formatar CNPJ - remover pontos e traços
                cnpj = ''.join(filter(str.isdigit, cgce_emp if cgce_emp else ""))
                
                # Verificar se a empresa já existe pelo código
                existing_company = Company.query.filter_by(codi_emp=codi_emp).first()
                
                if existing_company:
                    # Atualizar empresa existente
                    existing_company.name = apel_emp
                    existing_company.cnpj = cnpj
                    companies_updated += 1
                else:
                    # Criar nova empresa com o modelo simplificado
                    new_company = Company(
                        name=apel_emp,
                        cnpj=cnpj,
                        codi_emp=codi_emp
                    )
                    db.session.add(new_company)
                    companies_added += 1
                
                # Commit a cada 100 registros para evitar problemas de memória
                if (companies_added + companies_updated) % 100 == 0:
                    db.session.commit()
            
            except Exception as e:
                errors.append(f"Erro ao processar empresa {row[2] if row else 'desconhecida'}: {str(e)}")
        
        # Commit final
        db.session.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Importação de empresas concluída",
            "companies_added": companies_added,
            "companies_updated": companies_updated,
            "errors": errors
        }), 200
        
    except pyodbc.Error as e:
        return jsonify({
            "message": f"Erro de conexão ODBC: {str(e)}",
            "success": False
        }), 500
    except Exception as e:
        return jsonify({
            "message": f"Erro: {str(e)}",
            "success": False
        }), 500

@imports_bp.route('/employees/associate-by-code', methods=['POST'])
@admin_required
def associate_employees_by_code():
    """Associa funcionários às empresas com base no código de empresa (codi_emp)"""
    data = request.get_json()
    
    if not data or 'mappings' not in data:
        return jsonify({
            "message": "É necessário fornecer um mapeamento de códigos de empresa para IDs de empresa",
            "example": {
                "mappings": {
                    "1": "uuid-empresa-1",
                    "2": "uuid-empresa-2"
                }
            }
        }), 400
    
    mappings = data['mappings']
    results = {
        "total_updated": 0,
        "by_company": {},
        "errors": []
    }
    
    for codi_emp, company_id in mappings.items():
        try:
            # Encontrar todos os funcionários com este código de empresa
            employees = Employee.query.filter_by(codi_emp=codi_emp, company_id=None).all()
            
            for employee in employees:
                employee.company_id = company_id
            
            count = len(employees)
            results["total_updated"] += count
            results["by_company"][company_id] = count
            
        except Exception as e:
            results["errors"].append(f"Erro ao processar código {codi_emp}: {str(e)}")
    
    db.session.commit()
    
    return jsonify(results), 200

@imports_bp.route('/associate-employees-to-companies', methods=['POST'])
@admin_required
def associate_employees_to_companies():
    """Associa funcionários às empresas automaticamente com base no codi_emp"""
    try:
        # Encontrar funcionários sem empresa
        unassigned_employees = Employee.query.filter_by(company_id=None).all()
        
        assigned_count = 0
        not_found_count = 0
        errors = []
        
        for employee in unassigned_employees:
            try:
                if employee.codi_emp:
                    # Buscar empresa pelo código
                    company = Company.query.filter_by(codi_emp=employee.codi_emp).first()
                    
                    if company:
                        employee.company_id = company.id
                        assigned_count += 1
                    else:
                        not_found_count += 1
            except Exception as e:
                errors.append(f"Erro ao associar funcionário {employee.id}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            "message": "Associação concluída",
            "assigned_count": assigned_count,
            "not_found_count": not_found_count,
            "errors": errors
        }), 200
        
    except Exception as e:
        return jsonify({
            "message": f"Erro: {str(e)}",
            "success": False
        }), 500