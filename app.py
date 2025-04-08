from flask import Flask, render_template, request, redirect, session, url_for, flash
import requests
import os



app = Flask(__name__)
app.secret_key = "tu_clave_secreta"  # Define tu clave secreta aquí
API_BASE_URL = "http://127.0.0.1:9000"  # FastAPI corriendo en el puerto 9000
#API_BASE_URL = "https://apieccommunity-production.up.railway.app" #hosting en Railway


# ------------ Rutas Públicas ------------

@app.route('/')
def index():
    return render_template('auth/login.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Obtener datos del formulario
        email = request.form.get("email")
        password = request.form.get("password")

        # Preparar payload para FastAPI
        payload = {
            "Correo": email,
            "contrasena": password
        }

        try:
            # Hacer request a FastAPI (deberías tener un endpoint /login o similar)
            response = requests.post(f"{API_BASE_URL}/usuarios/login", json=payload)

            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            flash(f"Error al iniciar sesión: {http_err}", "danger")
            return redirect(url_for("login"))
        except Exception as err:
            flash(f"Ocurrió un error: {err}", "danger")
            return redirect(url_for("login"))

        # Si el login fue exitoso, redirige al dashboard
        session["user"] = response.json()  # o guarda token, etc.
        flash("Bienvenido/a de nuevo", "success")
        return redirect(url_for("dashboard"))

    # Si es GET, renderiza la vista
    return render_template("auth/login.html")


# Ruta de registro actualizada para GET y POST
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Obtener datos del formulario
        name = request.form.get("name")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")

        # Validar que las contraseñas coincidan
        if password != password_confirmation:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("register"))

        # ✅ Aquí está el payload con los nombres que espera FastAPI
        payload = {
            "Nombre": name,
            "Correo": email,
            "Ubicacion": "desconocido",
            "Rol": role,
            "Estado": "activo",
            "Cooldown": "0",
            "url_perfil": "default.jpg",
            "contrasena": password
        }

        try:
            response = requests.post(f"{API_BASE_URL}/usuarios", json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            flash(f"Error en el registro (HTTP): {http_err}", "danger")
            return redirect(url_for("register"))
        except Exception as err:
            flash(f"Error en el registro: {err}", "danger")
            return redirect(url_for("register"))

        flash("Usuario registrado exitosamente. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html")

@app.route('/logout')
def auth_logout():
    session.clear()  # Limpiar la sesión
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

# ------------ Rutas de usuario (requieren autenticación) ------------

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

# ------------ Rutas de administración ------------

@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/usuarios')
def admin_users():
    try:
        response = requests.get(f"{API_BASE_URL}/usuarios")
        response.raise_for_status()
        usuarios = response.json()
    except Exception as e:
        flash(f"Error al cargar usuarios: {e}", "danger")
        usuarios = []

    return render_template('admin/dashboard_users.html', usuarios=usuarios)

@app.route('/admin/usuarios/crear', methods=["GET", "POST"])
def crear_usuario():
    if request.method == "POST":
        data = {
            "Nombre": request.form.get("nombre"),
            "Correo": request.form.get("correo"),
            "Ubicacion": request.form.get("ubicacion"),
            "Rol": request.form.get("rol"),
            "Estado": request.form.get("estado"),
            "Cooldown": "0",
            "url_perfil": "default.jpg",
            "contrasena": request.form.get("contrasena")
        }

        try:
            response = requests.post(f"{API_BASE_URL}/usuarios", json=data)
            response.raise_for_status()
            flash("Usuario creado exitosamente", "success")
        except Exception as e:
            flash(f"Error al crear usuario: {e}", "danger")

        return redirect(url_for("admin_users"))

    return render_template("admin/form_usuario.html", modo="crear")

@app.route('/admin/usuarios/editar/<int:id>', methods=["GET", "POST"])
def editar_usuario(id):
    if request.method == "POST":
        data = {
            "Nombre": request.form.get("nombre"),
            "Ubicacion": request.form.get("ubicacion"),
            "Rol": request.form.get("rol"),
            "Estado": request.form.get("estado"),
            "Cooldown": request.form.get("cooldown"),
            "url_perfil": request.form.get("url_perfil"),
        }

        try:
            response = requests.put(f"{API_BASE_URL}/usuarios/{id}", json=data)
            response.raise_for_status()
            flash("Usuario actualizado correctamente", "success")
        except Exception as e:
            flash(f"Error al actualizar usuario: {e}", "danger")

        return redirect(url_for("admin_users"))

    try:
        response = requests.get(f"{API_BASE_URL}/usuarios/{id}")
        response.raise_for_status()
        usuario = response.json()
    except Exception as e:
        flash(f"No se pudo cargar el usuario: {e}", "danger")
        return redirect(url_for("admin_users"))

    return render_template("admin/form_usuario.html", usuario=usuario, modo="editar")

@app.route('/admin/usuarios/eliminar/<int:id>', methods=["POST"])
def eliminar_usuario(id):
    try:
        response = requests.post(f"{API_BASE_URL}/usuarios/{id}/delete")  # <-- este endpoint acepta POST
        response.raise_for_status()
        flash("Usuario eliminado correctamente", "success")
    except Exception as e:
        flash(f"No se pudo eliminar el usuario: {e}", "danger")

    return redirect(url_for("admin_users"))

@app.route('/admin/tiposreciclaje')
def admin_tiposreciclaje():
    try:
        response = requests.get(f"{API_BASE_URL}/tipos_reciclaje")
        response.raise_for_status()
        tipos = response.json()
    except Exception as e:
        flash(f"Error al cargar tipos de reciclaje: {e}", "danger")
        tipos = []

    return render_template('admin/tiposreciclaje.html', tipos=tipos)

# Crear nuevo tipo de reciclaje
@app.route('/admin/tiposreciclaje/crear', methods=["GET", "POST"])
def crear_tipo_reciclaje():
    if request.method == "POST":
        data = {
            "Nombre": request.form.get("nombre"),
            "PesoMinimo": request.form.get("peso_minimo"),
            "PesoMaximo": request.form.get("peso_maximo"),
            "PagoPorKg": request.form.get("pago_por_kg"),
            "GananciaPorKg": request.form.get("ganancia_por_kg")
        }

        try:
            response = requests.post(f"{API_BASE_URL}/tipos_reciclaje", json=data)
            response.raise_for_status()
            flash("Tipo de reciclaje creado exitosamente", "success")
        except Exception as e:
            flash(f"Error al crear tipo: {e}", "danger")

        return redirect(url_for("admin_tiposreciclaje"))

    return render_template("admin/form_tiposdereciclaje.html", modo="crear")

# Editar tipo de reciclaje
@app.route('/admin/tiposreciclaje/editar/<int:id>', methods=["GET", "POST"])
def editar_tipo_reciclaje(id):
    if request.method == "POST":
        data = {
            "Nombre": request.form.get("nombre"),
            "PesoMinimo": request.form.get("peso_minimo"),
            "PesoMaximo": request.form.get("peso_maximo"),
            "PagoPorKg": request.form.get("pago_por_kg"),
            "GananciaPorKg": request.form.get("ganancia_por_kg")
        }

        try:
            response = requests.put(f"{API_BASE_URL}/tipos_reciclaje/{id}", json=data)
            response.raise_for_status()
            flash("Tipo actualizado correctamente", "success")
        except Exception as e:
            flash(f"Error al actualizar tipo: {e}", "danger")

        return redirect(url_for("admin_tiposreciclaje"))

    try:
        response = requests.get(f"{API_BASE_URL}/tipos_reciclaje/{id}")
        response.raise_for_status()
        tipo = response.json()
    except Exception as e:
        flash(f"No se pudo cargar el tipo: {e}", "danger")
        return redirect(url_for("admin_tiposreciclaje"))

    return render_template("admin/form_tiposdereciclaje.html", tipo=tipo, modo="editar")

# Eliminar tipo
@app.route('/admin/tiposreciclaje/eliminar/<int:id>', methods=["POST"])
def eliminar_tipo_reciclaje(id):
    try:
        response = requests.delete(f"{API_BASE_URL}/tipos_reciclaje/{id}")
        response.raise_for_status()
        flash("Tipo eliminado correctamente", "success")
    except Exception as e:
        flash(f"No se pudo eliminar el tipo: {e}", "danger")

    return redirect(url_for("admin_tiposreciclaje"))



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
