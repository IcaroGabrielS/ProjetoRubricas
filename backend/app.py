from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, User, Group, Company, CompanyFile, GroupPermission, bcrypt
from config import Config
import os
from werkzeug.utils import secure_filename
from functools import wraps
import datetime

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

# Rota para registro de usuário (agora restrita a administradores)
@app.route('/api/register', methods=['POST'])
@admin_required
def register():
    data = request.get_json()
    
    # Verifica se o usuário já existe
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
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

# Rota para obter detalhes de um grupo
@app.route('/api/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
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

# Nova rota para gerenciar permissões de visualização de grupos (apenas admin)
@app.route('/api/groups/<int:group_id>/permissions', methods=['GET', 'POST', 'DELETE'])
@admin_required
def manage_group_permissions(group_id):
    group = Group.query.get_or_404(group_id)
    
    # GET - Listar permissões atuais
    if request.method == 'GET':
        permissions = GroupPermission.query.filter_by(group_id=group_id).all