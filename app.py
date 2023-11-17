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
            return "error"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "error"

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return "error"

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
        if not request.form.get("username"):
            return "error"

        elif not request.form.get("password"):
            return "error"

        elif not request.form.get("confirmation"):
            return "error"

        elif request.form.get("password") != request.form.get("confirmation"):
            return "error"

        rows = db.execute(
            "SELECT * FROM users WHERE username=?", request.form.get("username")
        )

        if len(rows) != 0:
           return "error"

        db.execute(
            "INSERT INTO users (username, password) VALUES(?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
        )

        rows = db.execute(
            "SELECT * FROM users WHERE username=?", request.form.get("username")
        )

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")


#Ruta para cerrar sesion
@app.route("/logout")
def logout():
    session.clear()
    return "adios"


#Ruta para el horario de clases
@app.route("/horario", methods=["GET", "POST"])
@login_required
def horario():
    if request.method=="POST":
        if not request.form.get("dia_semana"):
            return "error"
        if not request.form.get("hora_inicio"):
            return "error"
        if not request.form.get("hora_fin"):
            return "error"
        if not request.form.get("materia"):
            return "error"
        horarios=db.execute("INSERT INTO Horario (dia_semana, hora_inicio, hora_fin, materia, user_id) VALUES (:dia_semana,:hora_inicio, :hora_fin, :materia, :user_id)", dia_semana=request.form.get("dia_semana"), hora_inicio=request.form.get("hora_inicio"),hora_fin=request.form.get("hora_fin"), materia=request.form.get("materia"), user_id=session["user_id"])
        return "yei"
    else:
        return render_template("horario.html")


# Ruta para ingresar calificaciones
@app.route("/calificaciones", methods=["GET", "POST"])
@login_required
def calificaciones():
    if request.method == "POST":
        materia_id = request.form.get("materia_id")
        calificacion = request.form.get("calificacion")

        if not materia_id or not calificacion:
            flash("Por favor, completa todos los campos.", "error")
            return redirect("/calificaciones")

        # Verificar si ya existe una calificación para la materia seleccionada
        existing_calificacion = db.execute("SELECT id FROM calificaciones WHERE materia_id = :materia_id AND user_id = :user_id",
        materia_id=materia_id, user_id=session["user_id"])

        if existing_calificacion:
            return "error"

        db.execute("INSERT INTO calificaciones (materia_id, calificacion, user_id) VALUES (:materia_id, :calificacion, :user_id)",
        materia_id=materia_id, calificacion=calificacion, user_id=session["user_id"])

        flash("Calificación agregada correctamente", "success")
        return redirect("/calificaciones")

    else:
        # Obtener la lista de materias del horario del usuario
        materias = db.execute("SELECT id, materia FROM horario WHERE user_id = :user_id", user_id=session["user_id"])

        return render_template("calificaciones.html", materias=materias)


#Ruta para anotaciones
@app.route("/anotaciones", methods=["GET", "POST"])
@login_required
def anotaciones():
    if request.method=="POST":
        if not request.form.get("title"):
            return "error"
        if not request.form.get("content"):
            return "error"
        notitas=db.execute("INSERT INTO anotaciones (titulo, contenido, user_id) VALUES (:titulo, :contenido, :user_id)", titulo=request.form.get("title"), contenido=request.form.get("content"), user_id=session["user_id"])
        return "bien"
    else:
        return render_template("anotaciones.html")


#Ruta para la lista de tareas
@app.route("/tareas", methods=["GET", "POST"])
@login_required
def tareas():
    if request.method == "POST":
        task_content = request.form.get("task_content")
        db.execute("INSERT INTO tasks (content, user_id) VALUES (:content, :user_id)", content=task_content, user_id=session["user_id"])
        flash("Tarea agregada correctamente", "success")
        return redirect("/tareas")

    tasks = db.execute("SELECT * FROM tasks WHERE user_id = :user_id", user_id=session["user_id"])
    return render_template("pendientes.html", tasks=tasks)

#Para las tareas que ya estan completadas
@app.route("/complete_task/<int:task_id>")
@login_required
def complete_task(task_id):
    db.execute("UPDATE tasks SET completed = 1 WHERE id = :task_id", task_id=task_id)
    flash("Tarea completada correctamente", "success")
    return redirect("/tareas")

#Para borrar las tareas
@app.route("/delete_task/<int:task_id>")
@login_required
def delete_task(task_id):
    db.execute("DELETE FROM tasks WHERE id = :task_id", task_id=task_id)
    flash("Tarea eliminada correctamente", "success")
    return redirect("/tareas")



if __name__=="__main__":    
    app.run(debug=True)

