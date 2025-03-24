from flask import Blueprint, request, jsonify, send_from_directory, current_app
from models import db, CompanyFile, Company, User
from middleware.auth import admin_required, login_required, get_current_user, user_has_company_access
from utils.validation import is_valid_uuid
from utils.error_handling import handle_error
from werkzeug.utils import secure_filename
import os
import datetime

files_bp = Blueprint('files', __name__)

# Extensões permitidas
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'pdf'}

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    """Sanitiza o nome do arquivo para evitar path traversal"""
    # Remover qualquer caminho e manter apenas o nome do arquivo
    sanitized = os.path.basename(secure_filename(filename))
    return sanitized

@files_bp.route('/companies/<company_id>/files', methods=['POST'])
@admin_required
def upload_file(company_id):
    try:
        if not is_valid_uuid(company_id):
            return jsonify({'message': 'ID de empresa inválido'}), 400
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'message': 'Empresa não encontrada'}), 404
        
        if 'file' not in request.files:
            return jsonify({'message': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar tamanho do arquivo (limite de 50MB)
        if request.content_length > current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024):
            return jsonify({'message': 'Arquivo excede o tamanho máximo permitido de 50MB'}), 413
        
        if file and allowed_file(file.filename):
            filename = sanitize_filename(file.filename)
            company_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f'company_{company_id}')
            os.makedirs(company_folder, exist_ok=True)
            
            file_path = os.path.join(company_folder, filename)
            
            # Verificar se o arquivo já existe
            if os.path.exists(file_path):
                # Adicionar timestamp ao nome do arquivo para torná-lo único
                name, ext = os.path.splitext(filename)
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{name}_{timestamp}{ext}"
                file_path = os.path.join(company_folder, filename)
                
            file.save(file_path)
            
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
        
        return jsonify({'message': 'Tipo de arquivo não permitido. Formatos aceitos: CSV, XLS, XLSX, PDF'}), 400
    except Exception as e:
        db.session.rollback()
        return handle_error(e, client_message="Erro ao fazer upload do arquivo")

@files_bp.route('/companies/<company_id>/files', methods=['GET'])
@login_required
def list_company_files(company_id):
    try:
        if not is_valid_uuid(company_id):
            return jsonify({'message': 'ID de empresa inválido'}), 400
        
        user = get_current_user()
        company = Company.query.get(company_id)
        
        if not company:
            return jsonify({'message': 'Empresa não encontrada'}), 404
        
        if not user.is_admin and not user_has_company_access(user.id, company_id):
            return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
        
        files = CompanyFile.query.filter_by(company_id=company_id).all()
        
        return jsonify({
            'files': [file.to_dict() for file in files],
            'count': len(files)
        }), 200
    except Exception as e:
        return handle_error(e, client_message="Erro ao listar arquivos da empresa")

@files_bp.route('/files/<file_id>/download', methods=['GET'])
@login_required
def download_file(file_id):
    try:
        user = get_current_user()
        file_obj = CompanyFile.query.get(file_id)
        
        if not file_obj:
            return jsonify({'message': 'Arquivo não encontrado'}), 404
        
        if not user.is_admin and not user_has_company_access(user.id, file_obj.company_id):
            return jsonify({'message': 'Acesso não autorizado a este arquivo'}), 403
        
        # Verificar se o arquivo existe no sistema de arquivos
        company_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f'company_{file_obj.company_id}')
        file_path = os.path.join(company_folder, file_obj.filename)
        
        if not os.path.exists(file_path):
            return jsonify({'message': 'Arquivo não encontrado no sistema'}), 404
            
        return send_from_directory(company_folder, file_obj.filename, as_attachment=True)
    except Exception as e:
        return handle_error(e, client_message="Erro ao fazer download do arquivo")