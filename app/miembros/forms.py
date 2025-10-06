from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField,TextAreaField
from wtforms.validators import DataRequired, Email,ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Rol, Miembro
from flask_wtf.file import FileField, FileAllowed

def roles_query():
    return Rol.query.all()

def lideres_query(exclude_id=None):
    query = Miembro.query.join(Rol).filter(Rol.nombre != 'Discipulo')
    if exclude_id:
        query = query.filter(Miembro.id != exclude_id)
    return query.order_by(Miembro.nombre_completo.asc()).all()

class MiembroForm(FlaskForm):
    nombre_completo = StringField('Nombre Completo', validators=[DataRequired()])
    fecha_ingreso = DateField('Fecha de Ingreso', format='%Y-%m-%d', validators=[DataRequired()])
    rol = QuerySelectField('Rol', query_factory=roles_query, get_label='nombre', allow_blank=False, validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    descripcion = TextAreaField('Descripción')
    foto = FileField('Foto de Perfil', validators=[FileAllowed(['jpg', 'png', 'jpeg'], '¡Solo imágenes!')])
     # allow_blank=True permite que un miembro no tenga líder (ej. el Pastor Principal)
    lider = QuerySelectField('Líder Asignado', 
                             get_label=lambda miembro: f"{miembro.nombre_completo} - {miembro.rol.nombre}", 
                             allow_blank=True)
    submit = SubmitField('Guardar Miembro')

    # --- ¡AQUÍ ESTÁ LA LÓGICA DEL DESAFÍO! ---
    def __init__(self, miembro_original=None, *args, **kwargs):
        super(MiembroForm, self).__init__(*args, **kwargs)
        # Guardamos el miembro que se está editando para poder compararlo.
        # Si es un miembro nuevo, esto será None.
        self.miembro_original = miembro_original

    def validate_lider(self, lider):
        # WTForms llama a esta función automáticamente para el campo 'lider'.
        lider_seleccionado = lider.data
        
        # 1. Nos aseguramos de que se haya seleccionado un líder.
        if not lider_seleccionado:
            return

        # 2. Verificamos si estamos en modo edición Y si el líder no ha cambiado.
        # Si es el mismo líder, no hacemos la validación del cupo.
        if self.miembro_original and self.miembro_original.lider == lider_seleccionado:
            return

        # 3. Si es un líder nuevo (o estamos creando), verificamos el cupo.
        if lider_seleccionado.discipulos.count() >= 12:
            # ¡Esta es la magia! raise ValidationError muestra el error
            # justo debajo del campo 'lider' en el formulario.
            raise ValidationError(f'El líder "{lider_seleccionado.nombre_completo}" ya tiene el cupo de 12 discípulos lleno.')

