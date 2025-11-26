from flask import Flask, request
from flask_wtf.csrf import CSRFProtect, CSRFError

app = Flask(__name__)
app.secret_key = "supersecret123"   # Cámbiala si es producción

# Configuración de sesión para mantener el token CSRF válido
app.config['SESSION_COOKIE_SECURE'] = False  # True en producción con HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Sin límite de tiempo para el token
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_CHECK_DEFAULT'] = True

# Enable CSRF protection
csrf = CSRFProtect(app)

# Make csrf_token available in all templates
@app.context_processor
def inject_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return dict(csrf_token=generate_csrf)

# Manejo de errores CSRF
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    from flask import flash, redirect, url_for
    flash("Error de seguridad: El token CSRF ha expirado o es inválido. Por favor, recarga la página e intenta nuevamente.", "error")
    # Intentar redirigir a la página anterior o al dashboard
    if request.referrer:
        return redirect(request.referrer)
    return redirect(url_for('dashboard.index'))

# Importar y registrar todos los blueprints
# Import auth first to avoid circular import issues
from modules import auth
from modules import dashboard, formularios, edificios, salas, reservas, programas, usuarios, sanciones, bi

app.register_blueprint(auth.auth_bp)
app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(formularios.formularios_bp)
app.register_blueprint(edificios.edificios_bp)
app.register_blueprint(salas.salas_bp)
app.register_blueprint(reservas.reservas_bp)
app.register_blueprint(programas.programas_bp)
app.register_blueprint(usuarios.usuarios_bp)
app.register_blueprint(sanciones.sanciones_bp)
app.register_blueprint(bi.bi_bp)

# Cargar datos de prueba al iniciar
if __name__ == "__main__":
    try:
        from init_datos_prueba import cargar_datos_prueba
        cargar_datos_prueba()
    except Exception as e:
        print(f"⚠️  No se pudieron cargar datos de prueba: {e}")
    
    app.run(debug=True, host="0.0.0.0")
    
