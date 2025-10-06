from app import create_app,db
from app.models import User
app = create_app()

@app.cli.command("crear-admin")
def crear_admin():
    """Asigna el rol de administrador a un usuario existente."""
    email = input("Introduce el email del usuario que será administrador: ")
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"¡Éxito! El usuario {user.email} ahora es administrador.")
    else:
        print(f"Error: No se encontró ningún usuario con el email {email}.")

if __name__ == '__main__':
    # El modo debug nos dará más información de errores y reiniciará el servidor automáticamente con cada cambio.
    app.run(debug=True)