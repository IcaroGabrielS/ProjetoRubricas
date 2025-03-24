from flask import Flask, jsonify
from flask_cors import CORS
from models import db, bcrypt, User
from config import Config
import os

def create_app(config_class=Config):
    """Factory function para criar e configurar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configuração para upload de arquivos
    UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
    
    # Certifica-se de que a pasta instance existe
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    
    # Inicializa extensões
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Importa as blueprints após inicialização para evitar imports circulares
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.companies import companies_bp
    from routes.employees import employees_bp
    from routes.files import files_bp
    from routes.imports import imports_bp
    
    # Registra as blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(companies_bp, url_prefix='/api')
    app.register_blueprint(employees_bp, url_prefix='/api')
    app.register_blueprint(files_bp, url_prefix='/api')
    app.register_blueprint(imports_bp, url_prefix='/api')
    
    # Cria as tabelas no banco de dados e inicializa o admin
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    # Adiciona tratamento global de erros
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Erro não tratado: {str(e)}")
        return jsonify({"message": "Erro interno do servidor"}), 500
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"message": "Recurso não encontrado"}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"message": "Método não permitido"}), 405
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"message": "Requisição inválida"}), 400
    
    return app

def create_admin_user():
    """Cria um usuário admin se não existir"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password='admin123', is_admin=True)
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)