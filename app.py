from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "clave-secreta-super-segura-1114"

# Configuración BD
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    programa = db.Column(db.String(50), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Estudiante {self.nombre}>'


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # profesor o estudiante

    def establecer_contraseña(self, contraseña):
        self.contraseña = generate_password_hash(contraseña)

    def verificar_contraseña(self, contraseña):
        return check_password_hash(self.contraseña, contraseña)

    def __repr__(self):
        return f'<Usuario {self.usuario}>'


class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    creada_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.now())

    profesor = db.relationship('Usuario', backref='tareas')

    def __repr__(self):
        return f'<Tarea {self.titulo}>'


# Crear tablas y usuario profesor
with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(usuario="henry").first():
        profesor = Usuario(usuario="henry", rol="profesor")
        profesor.establecer_contraseña("password123")
        db.session.add(profesor)
        db.session.commit()
        print("Profesor creado")



# RUTAS 


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/informacion")
def informacion():
    datos = {
        "aula": "215",
        "profesor": "Henry Ortegon",
        "horario": "Miercoles 16:45-18:10 | Jueves 12:30-14:20",
        "objetivos": [
            "Aprender Python básico",
            "Entender Flask",
            "Construir un portal web real"
        ]
    }
    return render_template("informacion.html", **datos)


@app.route("/recursos")
def recursos():
    enlaces = [
        {"nombre": "Documentación Flask", "url": "https://flask.palletsprojects.com"},
        {"nombre": "Tutorial Python", "url": "https://docs.python.org"},
        {"nombre": "GitHub del Profesor", "url": "https://github.com/hortegon"}
    ]
    return render_template("recursos.html", enlaces=enlaces)


@app.route("/tareas")
def tareas_publicas():
    lista_tareas = [
        {"numero": 1, "titulo": "Portal base", "fecha": "25/05/2026"},
        {"numero": 2, "titulo": "Datos dinámicos", "fecha": "30/05/2026"},
        {"numero": 3, "titulo": "Múltiples páginas", "fecha": "05/06/2026"}
    ]
    return render_template("tareas.html", tareas=lista_tareas)



# INSCRIPCIÓN


@app.route("/inscripcion", methods=["GET", "POST"])
def inscripcion():
    mensaje = None

    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        programa = request.form.get("programa")

        if not nombre or not email or not programa:
            mensaje = "Por favor completa todos los campos."
        else:
            try:
                nuevo = Estudiante(nombre=nombre, email=email, programa=programa)
                db.session.add(nuevo)
                db.session.commit()
                mensaje = f"Bienvenido {nombre}, te has registrado correctamente."
            except:
                db.session.rollback()
                mensaje = "Error: este email ya está registrado."

    return render_template("inscripcion.html", mensaje=mensaje)


@app.route("/estudiantes")
def estudiantes():
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))

    lista = Estudiante.query.all()
    return render_template("estudiantes.html", estudiantes=lista)


# LOGIN


@app.route("/login", methods=["GET", "POST"])
def login():
    mensaje = None

    if request.method == "POST":
        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")

        user = Usuario.query.filter_by(usuario=usuario).first()

        if user and user.verificar_contraseña(contraseña):
            session['usuario_id'] = user.id
            session['usuario_nombre'] = user.usuario
            session['rol'] = user.rol

            if user.rol == "profesor":
                return redirect(url_for("panel_profesor"))
            else:
                return redirect(url_for("panel_estudiante"))
        else:
            mensaje = "Usuario o contraseña incorrectos."

    return render_template("login.html", mensaje=mensaje)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))



# PANEL PROFESOR


@app.route("/panel-profesor")
def panel_profesor():
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))

    return render_template("panel_profesor.html", usuario=session['usuario_nombre'])


@app.route("/crear-tarea", methods=["GET", "POST"])
def crear_tarea():
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))

    if request.method == "POST":
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        fecha_entrega = request.form.get("fecha_entrega")

        nueva = Tarea(
            titulo=titulo,
            descripcion=descripcion,
            fecha_entrega=fecha_entrega,
            creada_por=session['usuario_id']
        )

        db.session.add(nueva)
        db.session.commit()

        return redirect(url_for("mis_tareas"))

    return render_template("crear_tarea.html")


@app.route("/mis-tareas")
def mis_tareas():
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))

    tareas = Tarea.query.all()
    return render_template("mis_tareas.html", tareas=tareas)


@app.route("/editar-tarea/<int:id>", methods=["GET", "POST"])
def editar_tarea(id):
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))

    tarea = Tarea.query.get_or_404(id)

    if request.method == "POST":
        tarea.titulo = request.form.get("titulo")
        tarea.descripcion = request.form.get("descripcion")
        tarea.fecha_entrega = request.form.get("fecha_entrega")

        db.session.commit()
        return redirect(url_for("mis_tareas"))

    return render_template("editar_tarea.html", tarea=tarea)


@app.route("/eliminar-tarea/<int:id>")
def eliminar_tarea(id):
    if 'rol' not in session or session['rol'] != 'profesor':
        return redirect(url_for("login"))

    tarea = Tarea.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()

    return redirect(url_for("mis_tareas"))


# PANEL ESTUDIANTE

@app.route("/panel-estudiante")
def panel_estudiante():
    if 'rol' not in session or session['rol'] != 'estudiante':
        return redirect(url_for("login"))

    tareas = Tarea.query.all()
    return render_template("panel_estudiante.html", usuario=session['usuario_nombre'], tareas=tareas)




if __name__ == '__main__':
    app.run(debug=True)
