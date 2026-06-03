

# Importamos Flask y una funcion que permite mostrar un HTML.
from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def inicio():
    # Datos del portal
    nombre_profesor = "Sara Montaño"
    email_profesor = "smontanoe093@inemkennedy.edu.co"
    horario = "Miercoles 16:45-18:10 | Jueves 12:30-14:20"
    aula = "215"
    descripcion = "Aprenderemos Python, Flask y construiremos un portal web real paso a paso "
    
    # Nuevas variables agregadas
    nombre = "Sara Montaño"
    edad = 16

    
    # Pasar los datos a la plantilla
    return render_template(
        "index.html",
        profesor=nombre_profesor,
        email=email_profesor,
        horario=horario,
        aula=aula,
        descripcion=descripcion,
        nombre=nombre,      # Enviado
        edad=edad           # Enviado 
    )


@app.route("/informacion")
def informacion():
    datos = {
        "aula": "215",
        "profesor": "Henry Ortegon",
        "horario": "Miercoles 16:45-18:10 | Jueves 12:30-14:20",
        "objetivos": [
            "Aprender Python basico",
            "Entender Flask y aplicaciones web",
            "Construir un portal web real"
        ]
    }
    return render_template("informacion.html", **datos)

@app.route("/recursos")
def recursos():
    enlaces = [
        {"nombre": "Documentacion Flask", "url": "https://flask.palletsprojects.com"},
        {"nombre": "Tutorial Python", "url": "https://docs.python.org"},
        {"nombre": "GitHub del Profesor", "url": "https://github.com/hortegon"}
    ]
    return render_template("recursos.html", enlaces=enlaces)

@app.route("/tareas")
def tareas():
    lista_tareas = [
        {"numero": 1, "titulo": "Portal base", "fecha": "25/05/2026"},
        {"numero": 2, "titulo": "Datos dinamicos", "fecha": "30/05/2026"},
        {"numero": 3, "titulo": "Multiple paginas", "fecha": "05/06/2026"}
    ]
    return render_template("tareas.html", tareas=lista_tareas)








if __name__ == '__main__':
    app.run(debug=True)


