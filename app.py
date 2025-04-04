from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_login import login_required
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret-key-default')
API_BASE_URL = os.getenv('FASTAPI_URL', 'http://localhost:8000')

# ------------ Rutas Públicas ------------
@app.route('/')
def index():
    return render_template('auth/login.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/register')
def register():
    return render_template('auth/register.html')

@app.route('/logout')
def auth_logout():
    session.clear()  # Limpiar la sesión
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

# Rutas de usuario (requieren autenticación)
@app.route('/dashboard')
def dashboard():
    return render_template('user/dashboard.html')

@app.route('/puntos-recoleccion')
def puntos_recoleccion():
    return render_template('user/puntos_recoleccion.html')

@app.route('/comunidad')
def comunidad():
    return render_template('user/comunidad.html')

@app.route('/comentarios')
def comentarios():
    return render_template('user/comentarios.html')

@app.route('/perfil')
def perfil():
    return render_template('user/perfil.html')

@app.route('/configuracion')
def configuracion():
    return render_template('user/configuracion.html')

# Rutas de administración
@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')


@app.route('/admin/usuarios')
def admin_users():
    return render_template('admin/dashboard_users.html')

@app.route('/admin/empresas')
def admin_companies():
    return render_template('admin/dashboard_companies.html')

@app.route('/admin/puntos-recoleccion')
def admin_pickup_points():
    return render_template('admin/dashboard_pickup_points.html')

@app.route('/admin/comunidad')
def admin_community():
    return render_template('admin/dashboard_community.html')

@app.route('/admin/notificaciones')
def admin_notifications():
    return render_template('admin/dashboard_notifications.html')

@app.route('/admin/ayuda')
def admin_help():
    return render_template('admin/dashboard_help.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)