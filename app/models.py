from . import db  # Importamos la instancia db desde el __init__.py de la app
from . import bcrypt # ¡Importa bcrypt desde nuestro paquete de la app!
from datetime import datetime
from app import login_manager # ¡Importa el login_manager aquí!
from flask_login import UserMixin # ¡Importante! Añade esta importación

class User(UserMixin,db.Model):
    __tablename__ = 'users' # Nombre de la tabla

    # Definimos las columnas
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False) # ¡Nueva columna!
    
    def __repr__(self):
        # Una representación útil para debugging
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'
    
@login_manager.user_loader
def load_user(user_id):
    # Flask-Login pasa el ID como string, así que lo convertimos a entero
    return User.query.get(int(user_id))


class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), unique=True)
    miembros = db.relationship('Miembro', backref='rol', lazy='dynamic')

    @staticmethod
    def insertar_roles():
        roles = ['Pastor', 'Lider de 12', 'Lider de Celula', 'Discipulo']
        for r in roles:
            rol = Rol.query.filter_by(nombre=r).first()
            if rol is None:
                rol = Rol(nombre=r)
                db.session.add(rol)
        db.session.commit()

    def __repr__(self):
        return f'<Rol {self.nombre}>'

class Miembro(db.Model):
    __tablename__ = 'miembros'
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fecha_ingreso = db.Column(db.Date, nullable=False)
    # Eliminamos el campo de rol anterior y añadimos la relación
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    descripcion = db.Column(db.String(200))
    foto_perfil = db.Column(db.String(128), nullable=True, default='default.png')
    lider_id = db.Column(db.Integer, db.ForeignKey('miembros.id'))

    # Relación para obtener la lista de discípulos de un líder
    # cascade="all, delete-orphan" significa que si se elimina un líder, sus discípulos también se verán afectados (se quedarán sin líder)
    discipulos = db.relationship('Miembro',
                                backref=db.backref('lider', remote_side=[id]),
                                lazy='dynamic',
                                cascade="all, delete-orphan")
    def __repr__(self):
        return f'<Miembro {self.nombre_completo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'rol': self.rol.nombre,
            'lider_id': self.lider_id,
            'foto_url': self.foto_perfil # Asumiendo que guardaste el nombre del archivo
        }