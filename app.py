from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app=Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


# Ruta de la pestaña principal
@app.route("/")
@login_required
def index():
    return render_template("index.html")


#Ruta del login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return redirect("/")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return redirect("/")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return redirect("/")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


#Ruta del registro
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":
        if not request.form.get("new_username"):
            return redirect("/register")

        elif not request.form.get("new_password"):
            return redirect("/register")

        elif not request.form.get("confirmation"):
            return redirect("/register")

        elif request.form.get("password") != request.form.get("confirmation"):
            return redirect("/register")

        rows = db.execute(
            "SELECT * FROM users WHERE username=?", request.form.get("username")
        )

        if len(rows) != 0:
           return redirect("/register")

        db.execute(
            "INSERT INTO users (username, password) VALUES(?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
        )

        rows = db.execute(
            "SELECT * FROM users WHERE username=?", request.form.get("username")
        )

        session["user_id"] = rows[0]["id"]

        return redirect("/login")

    else:
        return render_template("register.html")


#Ruta para cerrar sesion
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


#Ruta para el horario de clases
@app.route("/horario", methods=["GET", "POST"])
@login_required
def horario():
    if request.method=="POST":
        if not request.form.get("dia_semana"):
            return redirect("/horario")
        if not request.form.get("hora_inicio"):
            return redirect("/horario")
        if not request.form.get("hora_fin"):
            return redirect("/horario")
        if not request.form.get("materia"):
            return redirect("/horario")
        
        existing_schedule = db.execute("SELECT * FROM Horario WHERE user_id = :user_id AND dia_semana = :dia_semana AND hora_inicio = :hora_inicio",
        user_id=session["user_id"], dia_semana=request.form.get("dia_semana"), hora_inicio=request.form.get("hora_inicio"))

        if existing_schedule:
            return redirect("/horario")
        horarios=db.execute("INSERT INTO Horario (dia_semana, hora_inicio, hora_fin, materia, user_id) VALUES (:dia_semana,:hora_inicio, :hora_fin, :materia, :user_id)", dia_semana=request.form.get("dia_semana"), hora_inicio=request.form.get("hora_inicio"),hora_fin=request.form.get("hora_fin"), materia=request.form.get("materia"), user_id=session["user_id"])
    user_schedules = db.execute("SELECT * FROM Horario WHERE user_id = :user_id", user_id=session["user_id"])

    # Render the template with the user's schedules
    return render_template("horario.html", schedules=user_schedules)


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
        existing_calificacion = db.execute("SELECT id FROM calificaciones WHERE materia_id = :materia_id AND user_id = :user_id",
        materia_id=materia_id, user_id=session["user_id"])

        if existing_calificacion:
            return redirect("/calificaciones")

        # Insertar la nueva calificación en la base de datos
        db.execute("INSERT INTO calificaciones (materia_id, calificacion, user_id) VALUES (:materia_id, :calificacion, :user_id)",
                   materia_id=materia_id, calificacion=calificacion, user_id=session["user_id"])

        return redirect("/calificaciones")

    else:
        # Obtener la lista de materias del horario del usuario
        materias = db.execute("SELECT id, materia FROM horario WHERE user_id = :user_id", user_id=session["user_id"])

        # Obtener las calificaciones del usuario
        calificaciones = db.execute(
            "SELECT c.calificacion, h.materia FROM calificaciones c JOIN horario h ON c.materia_id = h.id WHERE c.user_id = :user_id",
            user_id=session["user_id"])

        return render_template("calificaciones.html", materias=materias, calificaciones=calificaciones)


#Ruta para anotaciones
@app.route("/anotaciones", methods=["GET", "POST"])
@login_required
def anotaciones():
    if request.method=="POST":
        if not request.form.get("title"):
            return redirect("/anotaciones")
        if not request.form.get("content"):
            return redirect("/anotaciones")
        notitas=db.execute("INSERT INTO anotaciones (titulo, contenido, user_id) VALUES (:titulo, :contenido, :user_id)", titulo=request.form.get("title"), contenido=request.form.get("content"), user_id=session["user_id"])
    anotaciones = db.execute("SELECT id, titulo, contenido FROM anotaciones WHERE user_id = :user_id", user_id=session["user_id"])
    return render_template("anotaciones.html", anotaciones=anotaciones)


#Ruta para borrar anotaciones
@app.route("/eliminar_anotacion/<int:anotacion_id>", methods=["POST"])
@login_required
def eliminar_anotacion(anotacion_id):
    # Obtener la anotación a eliminar
    anotacion = db.execute("SELECT * FROM anotaciones WHERE id = :anotacion_id AND user_id = :user_id",
    anotacion_id=anotacion_id, user_id=session["user_id"])

    if anotacion:
        # Eliminar la anotación
        db.execute("DELETE FROM anotaciones WHERE id = :anotacion_id", anotacion_id=anotacion_id)

    return redirect("/anotaciones")


#Ruta para la lista de tareas
@app.route("/tareas")
@login_required
def tareas():
    return render_template("tareas.html")





if __name__=="__main__":    
    app.run(debug=True)

