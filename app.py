from cs50 import SQL
import regex
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__)

# Configurar la sesión para usar el sistema de archivos (en lugar de cookies firmadas)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configurar la biblioteca CS50 para usar la base de datos SQLite
db = SQL("sqlite:///database.db")


# Ruta para la pestaña principal
@app.route("/")
@login_required
def index():
    return render_template("index.html")


# Ruta para el inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    """Iniciar sesión del usuario"""

    # Olvidar cualquier user_id
    session.clear()

    # El usuario llegó a la ruta a través de POST (al enviar un formulario por POST)
    if request.method == "POST":
        # Asegurarse de que se haya enviado un nombre de usuario
        if not request.form.get("username"):
            return render_template("login.html", data="No ingresó un usuario")

        # Asegurarse de que se haya enviado una contraseña
        elif not request.form.get("password"):
            return render_template("login.html", data="No ingresó una contraseña")

        # Consultar la base de datos para obtener el nombre de usuario
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Asegurarse de que el nombre de usuario exista y la contraseña sea correcta
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return render_template("login.html", data="Contraseña o usuario incorrecto")

        # Recordar qué usuario ha iniciado sesión
        session["user_id"] = rows[0]["id"]

        # Redirigir al usuario a la página de inicio
        return redirect("/")

    # El usuario llegó a la ruta a través de GET (al hacer clic en un enlace o redirección)
    else:
        return render_template("login.html")


# Ruta para el registro de usuarios
@app.route("/register", methods=["POST"])
def register():
    """Registrar usuario"""
    session.clear()

    # Verificar si se han enviado los campos necesarios
    if not request.form.get("new_username"):
        return redirect("/login")

    elif not request.form.get("new_password"):
        return redirect("/login")

    elif not request.form.get("confirmation"):
        return redirect("/login")

    elif request.form.get("new_password") != request.form.get("confirmation"):
        return render_template("login.html", data="Las contraseñas no coiciden")

    elif not validate_password(request.form.get("new_password")):
        return render_template("login.html", data="La contraseña no es segura")

    # Validar el nombre de usuario
    new_username = request.form.get("new_username")
    if len(new_username) < 8 or not any(char.isdigit() for char in new_username):
        return render_template("login.html", data="El usuario debe llevar mínimo 8 caracteres y 1 número")

    # Verificar si el nombre de usuario ya existe
    rows = db.execute(
        "SELECT * FROM users WHERE username=?", request.form.get("new_username")
    )

    if len(rows) != 0:
        return render_template("login.html", data="El usuario ya existe")

    # Insertar el nuevo usuario en la base de datos
    db.execute(
        "INSERT INTO users (username, password) VALUES(?, ?)",
        request.form.get("new_username"),
        generate_password_hash(request.form.get("new_password")),
    )

    # Iniciar sesión con el nuevo usuario
    rows = db.execute(
        "SELECT * FROM users WHERE username=?", request.form.get("new_username")
    )
    session["user_id"] = rows[0]["id"]

    return redirect("/login")


# Ruta para cerrar sesión
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# Ruta para el horario de clases
@app.route("/horario", methods=["GET", "POST"])
@login_required
def horario():
    if request.method == "POST":
        if not request.form.get("dia_semana"):
            return redirect("/horario")
        if not request.form.get("hora_inicio"):
            return redirect("/horario")
        if not request.form.get("hora_fin"):
            return redirect("/horario")
        if not request.form.get("materia"):
            return redirect("/horario")

        existing_schedule = db.execute(
            "SELECT * FROM Horario WHERE user_id = :user_id AND dia_semana = :dia_semana AND hora_inicio = :hora_inicio",
            user_id=session["user_id"],
            dia_semana=request.form.get("dia_semana"),
            hora_inicio=request.form.get("hora_inicio"),
        )

        if existing_schedule:
            return redirect("/horario")
        horarios = db.execute(
            "INSERT INTO Horario (dia_semana, hora_inicio, hora_fin, materia, user_id) VALUES (:dia_semana,:hora_inicio, :hora_fin, :materia, :user_id)",
            dia_semana=request.form.get("dia_semana"),
            hora_inicio=request.form.get("hora_inicio"),
            hora_fin=request.form.get("hora_fin"),
            materia=request.form.get("materia"),
            user_id=session["user_id"],
        )
    user_schedules = db.execute(
        "SELECT * FROM Horario WHERE user_id = :user_id", user_id=session["user_id"]
    )

    # Renderizar la plantilla con los horarios del usuario
    return render_template("horario.html", schedules=user_schedules)


#Ruta para borrar horario
@app.route("/borrar_horario", methods=[ "POST"])
@login_required
def horario_borrar():
    id_horario = request.form.get("id_materia") 
    db.execute(
            "DELETE FROM horario WHERE id = :id_materia",
            id_materia=id_horario,
        )
    
    return redirect('/horario')
    


# Ruta para ingresar calificaciones
@app.route("/calificaciones", methods=["GET", "POST"])
@login_required
def calificaciones():
    if request.method == "POST":
        materia_id = request.form.get("materia_id")
        calificacion = request.form.get("calificacion")

        # Validar que se ingresen valores para materia_id y calificacion
        if not materia_id or not calificacion:
            return redirect("/calificaciones")

        try:
            # Intentar convertir la calificacion a un número decimal
            calificacion = float(calificacion)
        except ValueError:
            # Manejar la excepción si no se puede convertir a un número
            return redirect("/calificaciones")

        # Validar el rango de la calificación (de 0 a 100)
        if not 0 <= calificacion <= 100:
            return redirect("/calificaciones")

        # Verificar si ya existe una calificación para la materia seleccionada
        existing_calificacion = db.execute(
            "SELECT id FROM calificaciones WHERE materia_id = :materia_id AND user_id = :user_id",
            materia_id=materia_id,
            user_id=session["user_id"],
        )

        if existing_calificacion:
            return redirect("/calificaciones")

        # Insertar la nueva calificación en la base de datos
        db.execute(
            "INSERT INTO calificaciones (materia_id, calificacion, user_id) VALUES (:materia_id, :calificacion, :user_id)",
            materia_id=materia_id,
            calificacion=calificacion,
            user_id=session["user_id"],
        )

        return redirect("/calificaciones")

    else:
        # Obtener la lista de materias del horario del usuario
        materias = db.execute(
            "SELECT id, materia FROM horario WHERE user_id = :user_id",
            user_id=session["user_id"],
        )

        # Obtener las calificaciones del usuario
        calificaciones = db.execute(
            "SELECT c.calificacion, h.materia FROM calificaciones c JOIN horario h ON c.materia_id = h.id WHERE c.user_id = :user_id",
            user_id=session["user_id"],
        )

        return render_template(
            "calificaciones.html", materias=materias, calificaciones=calificaciones
        )


#Ruta para borrar calificaciones
@app.route("/borrar_calificaciones", methods=[ "POST"])
@login_required
def calificacion_borrar():
    id_nota = request.form.get("id_calificacion") 
    db.execute(
            "DELETE FROM calificaciones WHERE id = :id_calificacion",
            id_calificacion=id_nota,
        )
    
    return redirect('/calificaciones')

# Ruta para anotaciones
@app.route("/anotaciones", methods=["GET", "POST"])
@login_required
def anotaciones():
    if request.method == "POST":
        if not request.form.get("title"):
            return redirect("/anotaciones")
        if not request.form.get("content"):
            return redirect("/anotaciones")
        notitas = db.execute(
            "INSERT INTO anotaciones (titulo, contenido, user_id) VALUES (:titulo, :contenido, :user_id)",
            titulo=request.form.get("title"),
            contenido=request.form.get("content"),
            user_id=session["user_id"],
        )
        flash("Anotación agregada con éxito.", "success")
        return redirect("/anotaciones")
    anotaciones = db.execute(
        "SELECT id, titulo, contenido FROM anotaciones WHERE user_id = :user_id",
        user_id=session["user_id"],
    )
    return render_template("anotaciones.html", anotaciones=anotaciones)


# Ruta para borrar anotaciones
@app.route("/eliminar_anotacion/<int:anotacion_id>", methods=["POST"])
@login_required
def eliminar_anotacion(anotacion_id):
    # Obtener la anotación a eliminar
    anotacion = db.execute(
        "SELECT * FROM anotaciones WHERE id = :anotacion_id AND user_id = :user_id",
        anotacion_id=anotacion_id,
        user_id=session["user_id"],
    )

    if anotacion:
        # Eliminar la anotación
        db.execute(
            "DELETE FROM anotaciones WHERE id = :anotacion_id",
            anotacion_id=anotacion_id,
        )

    return redirect("/anotaciones")


# Ruta para la lista de tareas
@app.route("/tareas")
@login_required
def tareas():
    return render_template("tareas.html")


#Funcion para validar la contraseña
def validate_password(password):
    if not regex.match(
        r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
        password,
    ):
        return False
    return True


if __name__ == "__main__":
    app.run(debug=True)
