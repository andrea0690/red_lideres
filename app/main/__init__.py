from flask import Blueprint

# Creamos el Blueprint.
# El primer argumento, 'main', es el nombre del Blueprint.
# El segundo, __name__, ayuda a Flask a localizar el Blueprint.
main_bp = Blueprint('main', __name__)

# Importamos las rutas al final para evitar importaciones circulares.
from . import routes