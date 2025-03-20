from flask import Blueprint, request, jsonify, send_from_directory, current_app
from models import db, CompanyFile, Company, User
from middleware.auth import admin_required, user_has_group_access
from utils.validation import is_valid_uuid
from werkzeug.utils import secure_filename
import os

files_bp = Blueprint('files', __name__)

# Extensões permitidas
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_bp.route('/companies/<company_id>/files', methods=['POST'])
@admin_required
def upload_file(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    company = Company.query.get_or_404(company_id)
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        company_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f'company_{company_id}')
        os.makedirs(company_folder, exist_ok=True)
        
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
    
    return jsonify({'message': 'Tipo de arquivo não permitido'}), 400

@files_bp.route('/companies/<company_id>/files', methods=['GET'])
def list_company_files(company_id):
    if not is_valid_uuid(company_id):
        return jsonify({'message': 'ID de empresa inválido'}), 400
    
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    company = Company.query.get_or_404(company_id)
    
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a esta empresa'}), 403
    
    files = CompanyFile.query.filter_by(company_id=company_id).all()
    
    return jsonify({
        'files': [file.to_dict() for file in files]
    }), 200

@files_bp.route('/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    user_id = request.headers.get('User-ID')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    file_obj = CompanyFile.query.get_or_404(file_id)
    company = Company.query.get(file_obj.company_id)
    
    if not user.is_admin and not user_has_group_access(user_id, company.group_id):
        return jsonify({'message': 'Acesso não autorizado a este arquivo'}), 403
    
    company_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f'company_{file_obj.company_id}')
    return send_from_directory(company_folder, file_obj.filename, as_attachment=True)