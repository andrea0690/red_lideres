from flask import  render_template, flash, redirect, url_for,request
from flask_login import current_user, login_user, logout_user # ¡Importa las funciones!
from . import auth_bp
from .forms import LoginForm, RegistrationForm
from app.models import User
from app import db


@auth_bp.route('/login',methods = ['GET','POST'])
def login():
    # Si el usuario ya está autenticado, lo redirigimos a la página principal
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        # Buscamos al usuario por su email
        user = User.query.filter_by(email=form.email.data).first()

        # Verificamos si el usuario existe Y si la contraseña es correcta
        if user is None or not user.check_password(form.password.data):
            flash('Email o contraseña inválidos', 'danger')
            return redirect(url_for('auth.login'))

        # Si todo es correcto, iniciamos sesión con el usuario
        login_user(user, remember=form.remember_me.data)
        flash('¡Has iniciado sesión exitosamente!', 'success')

        # Redirigimos al usuario a la página que intentaba acceder, o al home
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.home'))

    return render_template('login.html', title='Iniciar Sesión', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('¡Felicidades, ahora eres un usuario registrado!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Registro', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado la sesión.', 'info')
    return redirect(url_for('main.home'))
