from flask import Blueprint, request, jsonify, current_app
from models import db, Employee, Company, CompanyPermission
from middleware.auth import admin_required, get_current_user
from utils.error_handling import handle_error
from utils.validation import is_valid_uuid
import pyodbc
import datetime
from sqlalchemy.exc import SQLAlchemyError

imports_bp = Blueprint('imports', __name__)

@imports_bp.route('/import/employees', methods=['POST'])
@admin_required
def import_employees():
    """Importa funcionários do sistema externo"""
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
        
        # Estabelecer conexão com timeout
        conn_str = ";".join([f"{k}={v}" for k, v in conn_params.items()])
        
        # Registrar informações importantes para auditoria
        current_app.logger.info(
            f"Iniciando importação de funcionários pelo usuário {get_current_user().username} "
            f"em {datetime.datetime.utcnow().isoformat()}"
        )
        
        conn = pyodbc.connect(conn_str, timeout=60)  # 60 segundos de timeout
        cursor = conn.cursor()
        
        # Executar a consulta com a coluna codi_emp (usando consultas parametrizadas)
        query = "SELECT i_empregados, nome, salario, cpf, admissao, I_AFASTAMENTOS, codi_emp FROM bethadba.foempregados"
        cursor.execute(query)
        
        # Processar resultados
        employees_added = 0
        employees_updated = 0
        errors = []
        
        # Iniciar a transação principal
        try:
            # Usar lotes para processamento mais eficiente
            batch_size = 100
            employees_batch = []
            
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
                        employees_batch.append(new_employee)
                        employees_added += 1
                    
                    # Adicionar funcionários em lotes para melhor performance
                    if len(employees_batch) >= batch_size:
                        db.session.add_all(employees_batch)
                        db.session.flush()  # Executa as consultas sem commit
                        employees_batch = []
                        
                        # Log de progresso
                        if (employees_added + employees_updated) % 1000 == 0:
                            current_app.logger.info(f"Importados {employees_added + employees_updated} funcionários")
                
                except Exception as e:
                    errors.append({
                        "id": row[0] if row else "unknown",
                        "error": str(e)
                    })
            
            # Adicionar funcionários restantes no último lote
            if employees_batch:
                db.session.add_all(employees_batch)
                db.session.flush()
            
            # Commit final se não houver erros críticos
            if len(errors) < employees_added + employees_updated * 0.05:  # Se menos de 5% dos registros tiveram erros
                db.session.commit()
                commit_status = "completo"
            else:
                db.session.rollback()
                commit_status = "falhou devido a muitos erros"
                
            cursor.close()
            conn.close()
            
            # Log de conclusão
            current_app.logger.info(
                f"Importação concluída (commit {commit_status}): {employees_added} adicionados, "
                f"{employees_updated} atualizados, {len(errors)} erros"
            )
            
            return jsonify({
                "message": f"Importação concluída com sucesso (commit {commit_status})",
                "employees_added": employees_added,
                "employees_updated": employees_updated,
                "errors_count": len(errors),
                "errors": errors[:50]  # Limitar o número de erros retornados
            }), 200
            
        except Exception as e:
            db.session.rollback()
            raise e
            
    except pyodbc.Error as e:
        db.session.rollback()
        current_app.logger.error(f"Erro de conexão ODBC: {str(e)}")
        return handle_error(e, 500, "Erro na conexão com banco de dados externo")
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_error(e, 500, "Erro ao salvar dados no banco de dados local")
    except Exception as e:
        db.session.rollback()
        return handle_error(e, 500, "Erro durante a importação de funcionários")

@imports_bp.route('/employees/unassigned', methods=['GET'])
@admin_required
def get_unassigned_employees():
    """Retorna todos os funcionários que não estão associados a nenhuma empresa"""
    try:
        # Paginação opcional
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        
        query = Employee.query.filter_by(company_id=None)
        
        # Pesquisa por nome (opcional)
        search = request.args.get('search')
        if search:
            query = query.filter(Employee.name.ilike(f'%{search}%'))
            
        # Ordenação (opcional)
        sort_by = request.args.get('sort_by', 'name')
        order = request.args.get('order', 'asc')
        
        if hasattr(Employee, sort_by):
            if order.lower() == 'desc':
                query = query.order_by(getattr(Employee, sort_by).desc())
            else:
                query = query.order_by(getattr(Employee, sort_by).asc())
                
        # Executar a paginação - Adaptado para ser compatível com diferentes versões do SQLAlchemy
        try:
            # SQLAlchemy 1.4+
            pagination = query.paginate(page=page, per_page=per_page)
        except TypeError:
            # SQLAlchemy antigo
            pagination = query.paginate(page, per_page)
        
        return jsonify({
            "count": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": per_page,
            "employees": [emp.to_dict() for emp in pagination.items]
        }), 200
    except Exception as e:
        return handle_error(e, client_message="Erro ao buscar funcionários não associados")

@imports_bp.route('/employees/assign', methods=['POST'])
@admin_required
def assign_employees():
    """Associa funcionários a uma empresa manualmente por IDs"""
    try:
        data = request.get_json()
        
        if not data or 'company_id' not in data or 'employee_ids' not in data:
            return jsonify({"message": "company_id e employee_ids são obrigatórios"}), 400
        
        company_id = data['company_id']
        employee_ids = data['employee_ids']
        
        if not is_valid_uuid(company_id):
            return jsonify({"message": "ID de empresa inválido"}), 400
            
        company = Company.query.get(company_id)
        if not company:
            return jsonify({"message": "Empresa não encontrada"}), 404
        
        if not isinstance(employee_ids, list):
            return jsonify({"message": "employee_ids deve ser uma lista"}), 400
        
        count = 0
        errors = []
        
        # Usar sistema de transações mais robusto
        try:
            # Validar IDs de funcionários antes de começar a transação
            valid_ids = []
            for emp_id in employee_ids:
                if not is_valid_uuid(emp_id):
                    errors.append(f"ID de funcionário inválido: {emp_id}")
                else:
                    valid_ids.append(emp_id)
            
            if not valid_ids:
                return jsonify({
                    "message": "Nenhum ID de funcionário válido fornecido",
                    "errors": errors
                }), 400
            
            # Iniciar transação
            for emp_id in valid_ids:
                try:
                    employee = Employee.query.get(emp_id)
                    if employee:
                        employee.company_id = company_id
                        count += 1
                    else:
                        errors.append(f"Funcionário com ID {emp_id} não encontrado")
                except Exception as e:
                    errors.append(f"Erro ao associar funcionário ID {emp_id}: {str(e)}")
            
            if count > 0:
                db.session.commit()
                current_app.logger.info(f"Usuário {get_current_user().username} associou {count} funcionários à empresa {company_id}")
            else:
                db.session.rollback()
                return jsonify({
                    "message": "Nenhum funcionário foi associado à empresa",
                    "errors": errors
                }), 400
            
            return jsonify({
                "message": f"{count} funcionários associados à empresa com sucesso",
                "success_count": count,
                "error_count": len(errors),
                "errors": errors
            }), 200
            
        except Exception as e:
            db.session.rollback()
            raise e
    except Exception as e:
        db.session.rollback()
        return handle_error(e, client_message="Erro ao associar funcionários à empresa")

@imports_bp.route('/employees/codes', methods=['GET'])
@admin_required
def list_employee_codes():
    """Lista todos os códigos de empresa (codi_emp) distintos dos funcionários sem associação"""
    try:
        # Query para obter códigos únicos de funcionários sem empresa associada
        codes = db.session.query(Employee.codi_emp, db.func.count(Employee.id).label('count'))\
            .filter(Employee.company_id.is_(None))\
            .group_by(Employee.codi_emp)\
            .all()
        
        result = {
            "total_unassigned": sum(count for _, count in codes if _ is not None),
            "codes": [{"code": code, "count": count} for code, count in codes if code]
        }
        
        return jsonify(result), 200
    except Exception as e:
        return handle_error(e, client_message="Erro ao listar códigos de empresa")

@imports_bp.route('/import/companies', methods=['POST'])
@admin_required
def import_companies():
    """Importa empresas do sistema externo"""
    try:
        # Parâmetros de conexão
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
        
        # Registrar informações importantes para auditoria
        current_app.logger.info(
            f"Iniciando importação de empresas pelo usuário {get_current_user().username} "
            f"em {datetime.datetime.utcnow().isoformat()}"
        )
        
        # Estabelecer conexão com timeout
        conn_str = ";".join([f"{k}={v}" for k, v in conn_params.items()])
        conn = pyodbc.connect(conn_str, timeout=60)
        cursor = conn.cursor()
        
        # Executar a consulta para importar empresas
        query = "SELECT cgce_emp, apel_emp, codi_emp FROM bethadba.geempre"
        cursor.execute(query)
        
        # Processar resultados
        companies_added = 0
        companies_updated = 0
        errors = []
        
        # Usar sistema de transações mais robusto
        try:
            batch_size = 50
            companies_batch = []
            
            user = get_current_user()
            
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
                        # Criar nova empresa
                        new_company = Company(
                            name=apel_emp,
                            cnpj=cnpj,
                            codi_emp=codi_emp,
                            created_by=user.id
                        )
                        companies_batch.append(new_company)
                        companies_added += 1
                    
                    # Adicionar empresas em lotes
                    if len(companies_batch) >= batch_size:
                        db.session.add_all(companies_batch)
                        db.session.flush()
                        companies_batch = []
                        
                        # Log de progresso
                        if (companies_added + companies_updated) % 500 == 0:
                            current_app.logger.info(f"Importadas {companies_added + companies_updated} empresas")
                
                except Exception as e:
                    errors.append({
                        "codi_emp": row[2] if row else "unknown",
                        "error": str(e)
                    })
            
            # Adicionar empresas restantes no último lote
            if companies_batch:
                db.session.add_all(companies_batch)
                db.session.flush()
            
            # Commit final se não houver erros críticos
            if len(errors) < (companies_added + companies_updated) * 0.05:  # Se menos de 5% dos registros tiveram erros
                db.session.commit()
                commit_status = "completo"
            else:
                db.session.rollback()
                commit_status = "falhou devido a muitos erros"
            
            cursor.close()
            conn.close()
            
            # Log de conclusão
            current_app.logger.info(
                f"Importação de empresas concluída (commit {commit_status}): {companies_added} adicionadas, "
                f"{companies_updated} atualizadas, {len(errors)} erros"
            )
            
            return jsonify({
                "message": f"Importação de empresas concluída (commit {commit_status})",
                "companies_added": companies_added,
                "companies_updated": companies_updated,
                "errors_count": len(errors),
                "errors": errors[:50]  # Limitar o número de erros retornados
            }), 200
        
        except Exception as e:
            db.session.rollback()
            raise e
            
    except pyodbc.Error as e:
        db.session.rollback()
        return handle_error(e, 500, "Erro na conexão com banco de dados externo")
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_error(e, 500, "Erro ao salvar dados no banco de dados local")
    except Exception as e:
        db.session.rollback()
        return handle_error(e, 500, "Erro durante a importação de empresas")

@imports_bp.route('/employees/associate-by-code', methods=['POST'])
@admin_required
def associate_employees_by_code():
    """Associa funcionários às empresas com base no código de empresa (codi_emp)"""
    try:
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
        
        # Validar UUIDs antes de iniciar a transação
        invalid_uuids = []
        for codi_emp, company_id in mappings.items():
            if not is_valid_uuid(company_id):
                invalid_uuids.append(codi_emp)
        
        if invalid_uuids:
            return jsonify({
                "message": "Detectados IDs de empresa inválidos",
                "invalid_codes": invalid_uuids
            }), 400
                
        # Iniciar a transação principal
        try:
            for codi_emp, company_id in mappings.items():
                try:
                    # Verificar se a empresa existe
                    company = Company.query.get(company_id)
                    if not company:
                        results["errors"].append(f"Empresa com ID {company_id} não encontrada")
                        continue
                    
                    # Encontrar todos os funcionários com este código de empresa
                    employees = Employee.query.filter_by(codi_emp=codi_emp, company_id=None).all()
                    
                    count = len(employees)
                    if count > 0:
                        for employee in employees:
                            employee.company_id = company_id
                        
                        results["total_updated"] += count
                        results["by_company"][company_id] = count
                        
                        # Log de atividade
                        current_app.logger.info(f"Associados {count} funcionários com código {codi_emp} à empresa {company_id}")
                    else:
                        results["by_company"][company_id] = 0
                    
                except Exception as e:
                    results["errors"].append(f"Erro ao processar código {codi_emp}: {str(e)}")
            
            if results["total_updated"] > 0:
                db.session.commit()
                current_app.logger.info(f"Total de {results['total_updated']} funcionários associados às empresas")
            else:
                db.session.rollback()
                return jsonify({
                    "message": "Nenhum funcionário foi associado",
                    "results": results
                }), 400
            
            return jsonify(results), 200
            
        except Exception as e:
            db.session.rollback()
            raise e
    except Exception as e:
        db.session.rollback()
        return handle_error(e, client_message="Erro ao associar funcionários às empresas por código")

@imports_bp.route('/associate-employees-to-companies', methods=['POST'])
@admin_required
def associate_employees_to_companies():
    """Associa funcionários às empresas automaticamente com base no codi_emp"""
    try:
        # Opções de configuração
        data = request.get_json() or {}
        batch_size = data.get('batch_size', 1000)  # Tamanho do lote para processamento
        
        # Iniciar transação principal
        try:
            # Encontrar funcionários sem empresa
            total_unassigned = Employee.query.filter_by(company_id=None).count()
            
            # Processar em lotes para evitar problemas de memória
            offset = 0
            assigned_count = 0
            not_found_count = 0
            errors = []
            
            while offset < total_unassigned:
                # Buscar um lote de funcionários
                employees = Employee.query.filter_by(company_id=None).limit(batch_size).offset(offset).all()
                
                for employee in employees:
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
                
                db.session.flush()  # Executar as consultas sem commit
                offset += batch_size
                
                # Log de progresso
                current_app.logger.info(f"Progresso: {offset}/{total_unassigned} funcionários processados")
            
            if assigned_count > 0:
                db.session.commit()
                current_app.logger.info(f"Total de {assigned_count} funcionários associados às empresas automaticamente")
            else:
                db.session.rollback()
                return jsonify({
                    "message": "Nenhum funcionário foi associado",
                    "not_found_count": not_found_count,
                    "error_count": len(errors)
                }), 400
            
            return jsonify({
                "message": "Associação concluída",
                "assigned_count": assigned_count,
                "not_found_count": not_found_count,
                "error_count": len(errors),
                "errors": errors[:50]  # Limitar o número de erros retornados
            }), 200
            
        except Exception as e:
            db.session.rollback()
            raise e
    except Exception as e:
        db.session.rollback()
        return handle_error(e, client_message="Erro ao associar funcionários às empresas")