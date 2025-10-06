# app/api/routes.py
from flask import jsonify, make_response
from . import api_bp
from app.models import Miembro
from flask import jsonify, request # Importa request
from sqlalchemy import or_ # Importa or_



@api_bp.route('/miembros')
def get_miembros():
    # Obtenemos el término de búsqueda de la URL (ej. /api/v1/miembros?search=ana)
    search_term = request.args.get('search', '', type=str)

    query = Miembro.query

    if search_term:
        query = query.filter(
            or_(
                Miembro.nombre_completo.ilike(f'%{search_term}%'),
                Miembro.email.ilike(f'%{search_term}%')
            )
        )

    miembros_obj = query.limit(10).all() # Limitamos a 10 para no sobrecargar

    miembros_dict_list = []
    for miembro in miembros_obj:
        miembros_dict_list.append({
            'id': miembro.id,
            'nombre_completo': miembro.nombre_completo,
            'email': miembro.email,
            'rol': miembro.rol.nombre
        })

    return jsonify(miembros=miembros_dict_list)




@api_bp.route('/miembros/<int:miembro_id>')
def get_miembro_by_id(miembro_id):
    miembro = Miembro.query.filter_by(id=miembro_id).first()
    if miembro:
        miembro_dict = miembro.to_dict()
        return jsonify(miembro=miembro_dict, status=True, mensaje='respuesta correcta')
    
    return make_response(jsonify(status=False, mensaje='miembro no encontrado'), 404)
