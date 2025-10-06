from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

# Creamos la instancia de la extensión SIN asociarla aún a la app
db = SQLAlchemy()
migrate = Migrate() # Instancia de Migrate
login_manager = LoginManager() # Instancia de LoginManager
bcrypt = Bcrypt() # Instancia de Bcrypt

def create_app():
    # Creamos la instancia de la aplicación Flask
    app = Flask(__name__)

    app.config.from_pyfile('../config.cfg')

    db.init_app(app)
    migrate.init_app(app, db) # Inicializa Migrate
    login_manager.init_app(app) # Inicializa LoginManager
    bcrypt.init_app(app) # Inicializa Bcryp

    # ¡Nueva línea! Le dice a Flask-Login cuál es la vista de login.
    login_manager.login_view = 'auth.login'
    # Opcional: Personaliza el mensaje de flash
    login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    with app.app_context():
         
        from .main import main_bp
        from .auth import auth_bp
        from .miembros import miembros_bp
        from .reportes import reports_bp
        from .api import api_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(miembros_bp)
        app.register_blueprint(reports_bp, url_prefix= '/reportes') # Le damos un prefijo a la URL
        app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app