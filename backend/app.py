from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, User, Group, Company, CompanyFile, GroupPermission, bcrypt
from config import Config
import os
from werkzeug.utils import secure_filename
from functools import wraps
import datetime
import uuid

# Inicializa a aplicação Flask
app = Flask(__name__)
app.config.from_object(Config)

# Configuração para upload de arquivos
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Extensões permitidas
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'pdf'}

# Certifica-se de que a pasta instance existe
os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

# Habilita CORS
CORS(app)

# Inicializa o banco de dados com a aplicação
db.init_app(app)
bcrypt.init_app(app)

# Cria as tabelas no primeiro acesso
with app.app_context():
    db.create_all()
    # Criar um usuário admin se não existir
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password='admin123', is_admin=True)
        db.session.add(admin)
        db.session.commit()

# Decorador para verificar se usuário é admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar o token ou ID de usuário na requisição
        user_id = request.headers.get('User-ID')
        if not user_id:
            return jsonify({"message": "Authentication required"}), 401
        
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({"message": "Admin access required"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Função auxiliar para verificar se um usuário tem acesso a um grupo
def user_has_group_access(user_id, group_id):
    user = User.query.get(user_id)
    
    # Admin tem acesso a todos os grupos
    if user and user.is_admin:
        return True
    
    # Verifica se o usuário comum tem permissão específica para o grupo
    permission = GroupPermission.query.filter_by(user_id=user_id, group_id=group_id).first()
    return permission is not None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Validação de UUID
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

# Rota para registro de usuário (agora restrita a administradores)
@app.route('/api/register', methods=['POST'])
@admin_required
def register():
    data = request.get_json()
    
    # Verifica se o usuário já existe
    existing_user = User.query.filter_by(username=data['username']).first()
    if (existing_user):
        return jsonify({'message': 'Username already exists'}), 400
    
    # Cria um novo usuário (admin pode definir se é admin ou não)
    new_user = User(
        username=data['username'],
        password=data['password'],
        is_admin=data.get('is_admin', False)  # Permite ao admin definir se o novo usuário é admin
    )
    
    # Salva o usuário no banco
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'user': new_user.to_dict()}), 201

# Rota para login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Busca o usuário pelo username
    user = User.query.filter_by(username=data['username']).first()
    
    # Verifica se o usuário existe e se a senha está correta
    if user and user.check_password(data['password']):
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'is_admin': user.is_admin
        }), 200
    
    return jsonify({'message': 'Invalid username or password'}), 401

# Rota para listar usuários (apenas admin)
@app.route('/api/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

# Rota para obter detalhes de um usuário específico (apenas admin)
@app.route('/api/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'user': user.to_dict()
    }), 200

# Rota para excluir usuários (apenas admin)
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    # Verifica se o usuário existe
    user_to_delete = User.query.get_or_404(user_id)
    
    # Verifica se é o próprio usuário tentando se excluir
    admin_id = request.headers.get('User-ID')
    if int(admin_id) == user_id:
        return jsonify({'message': 'Não é possível excluir seu próprio usuário'}), 400
    
    # Verifica se existem grupos criados por este usuário
    groups_created = Group.query.filter_by(created_by=user_id).all()
    
    # Podemos decidir se queremos impedir a exclusão ou transferir a propriedade
    # Neste exemplo, impedimos a exclusão se o usuário criou grupos
    if groups_created:
        return jsonify({'message': 'Não é possível excluir este usuário porque ele criou grupos'}), 400
    
    # Exclui as permissões de grupo associadas a este usuário
    GroupPermission.query.filter_by(user_id=user_id).delete()
    
    # Exclui o usuário
    db.session.delete(user_to_delete)
    db.session.commit()
    
    return jsonify({'message': 'Usuário excluído com sucesso'}), 200

# Rota para criar grupos (apenas admin)
@app.route('/api/groups', methods=['POST'])
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

# Rota para listar grupos
@app.route('/api/groups', methods=['GET'])
def list_groups():
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Se for admin, obtém todos os grupos
    if user.is_admin:
        groups = Group.query.all()
        group_list = [group.to_dict_with_permissions() for group in groups]
    else:
        # Para usuários comuns, busca apenas os grupos para os quais tem permissão
        permissions = GroupPermission.query.filter_by(user_id=user_id).all()
        allowed_group_ids = [permission.group_id for permission in permissions]
        groups = Group.query.filter(Group.id.in_(allowed_group_ids)).all()
        group_list = [group.to_dict() for group in groups]
    
    return jsonify({
        'groups': group_list
    }), 200

# Rota para obter detalhes de um grupo - atualizada para UUID
@app.route('/api/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    # Verifica se o group_id é um UUID válido
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
    
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Verifica se o usuário tem acesso ao grupo
    if not user.is_admin and not user_has_group_access(user_id, group_id):
        return jsonify({'message': 'Acesso não autorizado a este grupo'}), 403
    
    group = Group.query.get_or_404(group_id)
    
    # Se for admin, inclui informações de permissão
    if user.is_admin:
        group_dict = group.to_dict_with_permissions()
    else:
        group_dict = group.to_dict()
    
    # Adicionar empresas associadas
    companies = Company.query.filter_by(group_id=group_id).all()
    group_dict['companies'] = [company.to_dict() for company in companies]
    
    return jsonify({'group': group_dict}), 200

# Nova rota para gerenciar permissões de visualização de grupos (apenas admin) - atualizada para UUID
@app.route('/api/groups/<group_id>/permissions', methods=['GET', 'POST', 'DELETE'])
@admin_required
def manage_group_permissions(group_id):
    # Verifica se o group_id é um UUID válido
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
        
    group = Group.query.get_or_404(group_id)
    
    # GET - Listar permissões atuais
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
    
    # POST - Adicionar permissão para um usuário
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'message': 'user_id é necessário'}), 400
        
        user_id = data['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Verifica se já existe permissão
        existing = GroupPermission.query.filter_by(group_id=group_id, user_id=user_id).first()
        if existing:
            return jsonify({'message': 'Usuário já tem acesso a este grupo'}), 400
        
        # Adiciona permissão
        new_permission = GroupPermission(group_id=group_id, user_id=user_id)
        db.session.add(new_permission)
        db.session.commit()
        
        return jsonify({
            'message': 'Acesso concedido com sucesso',
            'permission': new_permission.to_dict()
        }), 201
    
    # DELETE - Remover permissão de um usuário
    elif request.method == 'DELETE':
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'message': 'user_id é necessário'}), 400
        
        user_id = data['user_id']
        
        # Verifica se existe permissão
        permission = GroupPermission.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not permission:
            return jsonify({'message': 'Usuário não tem acesso a este grupo'}), 404
        
        # Remove permissão
        db.session.delete(permission)
        db.session.commit()
        
        return jsonify({
            'message': 'Acesso removido com sucesso'
        }), 200

# Rota para criar empresas dentro de um grupo (apenas admin) - atualizada para UUID
@app.route('/api/groups/<group_id>/companies', methods=['POST'])
@admin_required
def create_company(group_id):
    # Verifica se o group_id é um UUID válido
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
        
    data = request.get_json()
    user_id = request.headers.get('User-ID')
    
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

# Rota para listar empresas de um grupo - atualizada para UUID
@app.route('/api/groups/<group_id>/companies', methods=['GET'])
def list_companies(group_id):
    # Verifica se o group_id é um UUID válido
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
        
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Verifica se o usuário tem acesso ao grupo
    if not user.is_admin and not user_has_group_access(user_id, group_id):
        return jsonify({'message': 'Acesso não autorizado a este grupo'}), 403
    
    # Lista empresas do grupo
    companies = Company.query.filter_by(group_id=group_id).all()
    
    return jsonify({
        'companies': [company.to_dict() for company in companies]
    }), 200

# Rota para excluir um grupo e todas as suas empresas - atualizada para UUID
@app.route('/api/groups/<group_id>', methods=['DELETE'])
@admin_required
def delete_group(group_id):
    # Verifica se o group_id é um UUID válido
    if not is_valid_uuid(group_id):
        return jsonify({'message': 'ID de grupo inválido'}), 400
        
    group = Group.query.get_or_404(group_id)
    
    # Exclui todas as permissões de grupo primeiro
    GroupPermission.query.filter_by(group_id=group_id).delete()
    
    # Exclui todas as empresas associadas ao grupo
    companies = Company.query.filter_by(group_id=group_id).all()
    for company in companies:
        CompanyFile.query.filter_by(company_id=company.id).delete()
        db.session.delete(company)
    
    # Exclui o grupo
    db.session.delete(group)
    db.session.commit()
    
    return jsonify({'message': 'Grupo excluído com sucesso'}), 200

# As demais rotas permanecem inalteradas...

# Rota para upload de arquivos para uma empresa
@app.route('/api/companies/<int:company_id>/files', methods=['POST'])
@admin_required
def upload_file(company_id):
    company = Company.query.get_or_404(company_id)
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Criar pasta para a empresa se não existir
        company_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'company_{company_id}')
        os.makedirs(company_folder, exist_ok=True)
        
        file_path = os.path.join(company_folder, filename)
        file.save(file_path)
        
        # Salvar referência no banco
        file_type = filename.rsplit('.', 1)[1].lower()
        new_file = CompanyFile(
            company_id=company_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'message': 'Arquivo enviado com sucesso',
            'file': new_file.to_dict()
        }), 201
    
    return jsonify({'message': 'Tipo de arquivo não permitido'}), 400

# Rota para download de arquivos
@app.route('/api/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    file_obj = CompanyFile.query.get_or_404(file_id)
    company = Company.query.get(file_obj.company_id)
    
    # Verificar se o usuário tem acesso ao grupo ao qual a empresa pertence
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a este arquivo'}), 403
    
    company_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'company_{file_obj.company_id}')
    return send_from_directory(company_folder, file_obj.filename, as_attachment=True)

# Rota para excluir uma empresa
@app.route('/api/companies/<int:company_id>', methods=['DELETE'])
@admin_required
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    
    # Exclui todos os arquivos associados à empresa
    CompanyFile.query.filter_by(company_id=company_id).delete()
    
    # Exclui a empresa
    db.session.delete(company)
    db.session.commit()
    
    return jsonify({'message': 'Empresa excluída com sucesso'}), 200

# Rota para trocar a senha de um usuário (admin pode trocar a senha de qualquer usuário, usuário comum pode trocar sua própria senha)
@app.route('/api/users/<int:user_id>/password', methods=['PUT'])
def change_password(user_id):
    data = request.get_json()
    current_user_id = request.headers.get('User-ID')
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    user_to_change = User.query.get_or_404(user_id)
    
    # Verifica se o usuário é admin ou se está tentando mudar sua própria senha
    if not current_user.is_admin and int(current_user_id) != user_id:
        return jsonify({'message': 'Acesso não autorizado'}), 403
    
    # Verifica se a nova senha foi fornecida
    if 'new_password' not in data:
        return jsonify({'message': 'Nova senha é necessária'}), 400
    
    # Atualiza a senha do usuário
    user_to_change.password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'}), 200

# Rota para obter detalhes de uma empresa específica
@app.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    company = Company.query.get_or_404(company_id)
    
    # Verificar se o usuário tem acesso ao grupo ao qual a empresa pertence
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
    
    # Obter arquivos associados à empresa
    files = CompanyFile.query.filter_by(company_id=company_id).all()
    
    company_dict = company.to_dict()
    company_dict['files'] = [file.to_dict() for file in files]
    
    return jsonify({'company': company_dict}), 200

# Rota para listar arquivos de uma empresa
@app.route('/api/companies/<int:company_id>/files', methods=['GET'])
def list_company_files(company_id):
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    company = Company.query.get_or_404(company_id)
    
    # Verificar se o usuário tem acesso ao grupo ao qual a empresa pertence
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
    
    files = CompanyFile.query.filter_by(company_id=company_id).all()
    
    return jsonify({
        'files': [file.to_dict() for file in files]
    }), 200