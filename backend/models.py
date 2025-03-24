from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime
import uuid

db = SQLAlchemy()
bcrypt = Bcrypt()

def generate_uuid():
    """Gera um UUID padrão"""
    return str(uuid.uuid4())

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.is_admin = is_admin
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "is_admin": self.is_admin
        }

class Company(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    codi_emp = db.Column(db.String(50), unique=True, nullable=True)  # Campo adicionado
    
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_companies')
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cnpj": self.cnpj,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "codi_emp": self.codi_emp
        }
    
    def to_dict_with_permissions(self):
        company_dict = self.to_dict()
        company_dict["allowed_users"] = [
            permission.user_id for permission in CompanyPermission.query.filter_by(company_id=self.id).all()
        ]
        return company_dict

class CompanyPermission(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    company_id = db.Column(db.String(36), db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    company = db.relationship('Company', backref='permissions')
    user = db.relationship('User', backref='company_permissions')
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'user_id', name='unique_company_permission'),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat()
        }

class Employee(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    company_id = db.Column(db.String(36), db.ForeignKey('company.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    i_empregados = db.Column(db.String(50), unique=True, nullable=True)
    salario = db.Column(db.Float, nullable=True)
    admissao = db.Column(db.Date, nullable=True)
    i_afastamentos = db.Column(db.String(50), nullable=True)
    codi_emp = db.Column(db.String(50), nullable=True)
    
    company = db.relationship('Company', backref='employees')
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cpf": self.cpf,
            "company_id": self.company_id,
            "created_at": self.created_at.isoformat(),
            "i_empregados": self.i_empregados,
            "salario": self.salario,
            "admissao": self.admissao.isoformat() if self.admissao else None,
            "i_afastamentos": self.i_afastamentos,
            "codi_emp": self.codi_emp
        }
    
class CompanyFile(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    company_id = db.Column(db.String(36), db.ForeignKey('company.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    company = db.relationship('Company', backref='files')
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "uploaded_at": self.uploaded_at.isoformat()
        }