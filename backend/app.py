from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, User, Store, StoreFile, bcrypt
from config import Config
import os
from werkzeug.utils import secure_filename
from functools import wraps

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota para registro de usuário
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Verifica se o usuário já existe
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    # Cria um novo usuário (por padrão não é admin)
    new_user = User(
        username=data['username'],
        password=data['password'],
        is_admin=False
    )
    
    # Salva o usuário no banco
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

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

# Rota para criar lojas (apenas admin)
@app.route('/api/stores', methods=['POST'])
@admin_required
def create_store():
    data = request.get_json()
    user_id = request.headers.get('User-ID')
    
    # Verificar se o owner_id existe
    owner_id = data.get('owner_id')
    owner = User.query.get(owner_id)
    if not owner:
        return jsonify({'message': 'Usuário dono não encontrado'}), 400
    
    new_store = Store(
        name=data['name'],
        state_registration=data['state_registration'],
        store_number=data['store_number'],
        address=data['address'],
        created_by=user_id,
        owner_id=owner_id
    )
    
    db.session.add(new_store)
    db.session.commit()
    
    return jsonify({
        'message': 'Store created successfully',
        'store': new_store.to_dict()
    }), 201

# Rota para listar lojas
@app.route('/api/stores', methods=['GET'])
def list_stores():
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Se for admin, mostrar todas as lojas
    if user.is_admin:
        stores = Store.query.all()
    else:
        # Se não for admin, mostrar apenas as lojas onde o usuário é dono
        stores = Store.query.filter_by(owner_id=user.id).all()
    
    return jsonify({
        'stores': [store.to_dict() for store in stores]
    }), 200

# Rota para obter detalhes de uma loja
@app.route('/api/stores/<int:store_id>', methods=['GET'])
def get_store(store_id):
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    store = Store.query.get_or_404(store_id)
    
    # Verificar se o usuário tem permissão para acessar esta loja
    if not user.is_admin and store.owner_id != user.id:
        return jsonify({'message': 'Acesso não autorizado a esta loja'}), 403
    
    store_dict = store.to_dict()
    
    # Adicionar arquivos associados
    files = StoreFile.query.filter_by(store_id=store_id).all()
    store_dict['files'] = [file.to_dict() for file in files]
    
    return jsonify({'store': store_dict}), 200

# Rota para upload de arquivos para uma loja
@app.route('/api/stores/<int:store_id>/files', methods=['POST'])
@admin_required
def upload_file(store_id):
    store = Store.query.get_or_404(store_id)
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Criar pasta para a loja se não existir
        store_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'store_{store_id}')
        os.makedirs(store_folder, exist_ok=True)
        
        file_path = os.path.join(store_folder, filename)
        file.save(file_path)
        
        # Salvar referência no banco
        file_type = filename.rsplit('.', 1)[1].lower()
        new_file = StoreFile(
            store_id=store_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': new_file.to_dict()
        }), 201
    
    return jsonify({'message': 'File type not allowed'}), 400

# Rota para download de arquivos
@app.route('/api/files/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file = StoreFile.query.get_or_404(file_id)
    directory = os.path.dirname(file.file_path)
    filename = os.path.basename(file.file_path)
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)