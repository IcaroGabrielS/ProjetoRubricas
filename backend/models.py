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

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state_registration = db.Column(db.String(50), nullable=False)  # Inscrição Estadual
    store_number = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamento com o criador (usuário administrador)
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_stores')
    # Relacionamento com o dono
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_stores')
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "state_registration": self.state_registration,
            "store_number": self.store_number,
            "address": self.address,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "owner_id": self.owner_id,
            "owner_username": self.owner.username if self.owner else None
        }

class StoreFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento com a loja
    store = db.relationship('Store', backref='files')
    
    def to_dict(self):
        return {
            "id": self.id,
            "store_id": self.store_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "uploaded_at": self.uploaded_at.isoformat()
        }