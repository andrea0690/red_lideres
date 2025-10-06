from flask import  render_template
from flask_login import login_required #importa el decorador
from . import main_bp
from app.models import Miembro , Rol
from app import db
from sqlalchemy.orm import aliased



@main_bp.route('/')
@login_required # ¡Este es el guardia de seguridad!
def home():
    # Creamos las variables que vamos a pasar a la plantilla
    titulo_dinamico = "¡Hola Mundo Cristiano!"
    lista_miembros = ["Juan Pérez", "Ana García", "Pedro López"]

    # Pasamos las variables a render_template como argumentos
    return render_template('index.html', titulo=titulo_dinamico, miembros=lista_miembros)

# La ruta para tu desafío del día 1
@main_bp.route('/bienvenido')
@login_required # ¡Este es el guardia de seguridad!
def bienvenida():
    return render_template('bienvenido.html')


@main_bp.route('/equipo')
@login_required # ¡Este es el guardia de seguridad!
def equipo():
    equipo = [
        {'nombre': 'Cleon Dia', 'rol': 'Pastor Principal','foto': 'imperio6.jpeg'},
        {'nombre': 'Salbor Harding', 'rol': 'Líder de Jóvenes', 'foto':'salvor.jpg'},
        {'nombre': 'Gari Seldon', 'rol': 'Líder de Alabanza','foto':'gari.jpg'}
    ]   
    return render_template('equipo.html', equipo = equipo)

@main_bp.route('/dashboard' )
@login_required
def dashboard():
    # --- CÁLCULO DE ESTADÍSTICAS ---

    # 1. Conteo total de miembros
    total_miembros = Miembro.query.count()

    # 2. Conteo de miembros por rol
    conteo_por_rol = db.session.query(
        Rol.id,
        Rol.nombre,
        db.func.count(Miembro.id).label('cantidad')
    ).outerjoin(Miembro, Miembro.rol_id == Rol.id).group_by(Rol.id, Rol.nombre).all()

    # 3. Miembros añadidos recientemente
    miembros_recientes = Miembro.query.order_by(Miembro.id.desc()).limit(5).all()

    # 4. Líderes con cupo lleno (12 discípulos)
    # Creamos un alias para la tabla de discípulos para que SQLAlchemy no se confunda
    DiscipuloAlias = aliased(Miembro)
    lideres_llenos = db.session.query(Miembro).join(
        DiscipuloAlias, Miembro.discipulos
    ).group_by(Miembro.id).having(
        db.func.count(DiscipuloAlias.id) >= 12
    ).all()

    return render_template('dashboard/dashboard.html', 
                           title='Dashboard',
                           total_miembros=total_miembros,
                           conteo_por_rol=conteo_por_rol,
                           miembros_recientes=miembros_recientes,
                           lideres_llenos=lideres_llenos)

@main_bp.route('/jerarquia')
@login_required
def jerarquia():
    # Tu lógica mejorada: Unimos Miembro con Rol y filtramos por el nombre del rol Y la ausencia de líder.
    lideres_principales = Miembro.query.join(Rol).filter(
        Rol.nombre == 'Pastor',
        Miembro.lider_id == None
    ).all()
    return render_template('jerarquia.html', lideres=lideres_principales, title='Jerarquía de L-iderazgo')