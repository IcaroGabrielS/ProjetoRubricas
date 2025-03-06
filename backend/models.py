from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.is_admin = is_admin
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "is_admin": self.is_admin
        }

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state_registration = db.Column(db.String(50), nullable=False)  # Inscrição Estadual
    cnpj = db.Column(db.String(18), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamento com o criador (usuário administrador)
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_companies')
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "state_registration": self.state_registration,
            "cnpj": self.cnpj,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }

class CompanyFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento com a empresa
    company = db.relationship('Company', backref='files')
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "uploaded_at": self.uploaded_at.isoformat()
        }