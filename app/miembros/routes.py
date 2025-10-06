# app/miembros/routes.py
from flask import render_template, flash, redirect, url_for,request, current_app
from flask_login import login_required
from . import miembros_bp
from .forms import MiembroForm, lideres_query
from app.models import Miembro, Rol
from app import db
import os
from werkzeug.utils import secure_filename
from flask import current_app
from sqlalchemy import or_
from app.decorators import admin_required

def guardar_foto(form_foto):
    random_hex = os.urandom(8).hex()
    _, f_ext = os.path.splitext(form_foto.filename)
    nombre_foto = random_hex + f_ext
    ruta_foto = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_foto)
    form_foto.save(ruta_foto)
    return nombre_foto

@miembros_bp.route('/miembros')
@login_required
@admin_required # ¡Protege la ruta!
def listar_miembros():

    page = request.args.get('page', 1, type=int)
    rol_id = request.args.get('rol_id', None, type=int)
    search_term = request.args.get('search', None, type=str) # ¡Obtenemos el término de búsqueda!

    query_base = Miembro.query
    
    if rol_id:
        query_base = query_base.filter(Miembro.rol_id == rol_id)

    # ¡NUEVA LÓGICA DE BÚSQUEDA!
    if search_term:
        # Usamos or_ para buscar en múltiples columnas
        query_base = query_base.filter(
            or_(
                Miembro.nombre_completo.ilike(f'%{search_term}%'),
                
            )
        )    

    pagination = query_base.order_by(
        Miembro.nombre_completo.asc()
    ).paginate(
        page=page,
        per_page=current_app.config['MIEMBROS_POR_PAGINA'],
        error_out=False
    )

    miembros = pagination.items

     # ¡AQUÍ ESTÁ EL CAMBIO!
    return render_template(
        'miembros/listar_miembros.html', 
        miembros=miembros, 
        pagination=pagination, 
        rol_id=rol_id,
        search_term=search_term # ¡Pasamos el término de búsqueda a la plantilla!
    )

@miembros_bp.route('/miembros/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_miembro():
    form = MiembroForm()
    form.lider.query_factory = lambda: lideres_query()
    if form.validate_on_submit():
        nombre_archivo_foto = 'default.png'
        if form.foto.data:
            nombre_archivo_foto = guardar_foto(form.foto.data)

        miembro = Miembro(
            nombre_completo=form.nombre_completo.data,
            fecha_ingreso=form.fecha_ingreso.data,
            rol=form.rol.data,
            email= form.email.data,
            descripcion= form.descripcion.data,
            foto_perfil=nombre_archivo_foto,
            lider=form.lider.data # Asignamos el objeto líder completo
        )
        db.session.add(miembro)
        db.session.commit()
        flash('¡Miembro añadido exitosamente!', 'success')
        return redirect(url_for('miembros.listar_miembros'))
    return render_template('miembros/nuevo_miembro.html', form=form, title='Nuevo Miembro')

@miembros_bp.route('/miembros/editar/<int:miembro_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_miembro(miembro_id):
    miembro = Miembro.query.get_or_404(miembro_id)
    form = MiembroForm(miembro_original=miembro, obj=miembro)
    # Ajustar dinámicamente la lista de líderes excluyendo al propio miembro
    form.lider.query_factory = lambda: lideres_query(exclude_id=miembro.id)
    
    if form.validate_on_submit():
        if form.foto.data:
            miembro.foto_perfil = guardar_foto(form.foto.data)

        miembro.nombre_completo = form.nombre_completo.data
        miembro.fecha_ingreso = form.fecha_ingreso.data
        miembro.rol = form.rol.data
        miembro.email = form.email.data
        miembro.descripcion = form.descripcion.data
        miembro.lider = form.lider.data
        db.session.commit()

        flash('¡Miembro actualizado exitosamente!', 'success')
        return redirect(url_for('miembros.ver_perfil', miembro_id=miembro.id))
    return render_template('miembros/editar_miembro.html', form=form, title='Editar Miembro' , miembro_id=miembro.id)

@miembros_bp.route('/ver_perfil/<int:miembro_id>')
@login_required
def ver_perfil(miembro_id):
    miembro = Miembro.query.get_or_404(miembro_id)
    return render_template('miembros/ver_perfil.html', miembro=miembro)

# app/miembros/routes.py

@miembros_bp.route('/miembros/eliminar/<int:miembro_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_miembro(miembro_id):
    # 1. Busca al miembro por su ID. Si no lo encuentra, muestra un error 404.
    miembro = Miembro.query.get_or_404(miembro_id)
    
    # 2. Prepara la eliminación del objeto en la sesión de la base de datos.
    db.session.delete(miembro)
    
    # 3. Confirma el cambio y lo hace permanente en la base de datos.
    db.session.commit()
    
    # 4. Muestra un mensaje de éxito al usuario.
    flash('Miembro eliminado exitosamente.', 'info')
    
    # 5. Redirige al usuario de vuelta a la lista de miembros.
    return redirect(url_for('miembros.listar_miembros'))