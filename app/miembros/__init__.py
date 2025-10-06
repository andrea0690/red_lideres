from flask import Blueprint

# Creamos el Blueprint.
# El primer argumento, 'main', es el nombre del Blueprint.
# El segundo, __name__, ayuda a Flask a localizar el Blueprint.
miembros_bp = Blueprint('miembros', __name__, template_folder='templates')

# Importamos las rutas al final para evitar importaciones circulares.
from . import routes