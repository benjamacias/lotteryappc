import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from models import db, Client, Debt, Payment, User, Movement

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")
bcrypt = Bcrypt(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "clients.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(
            username="admin",
            password_hash=bcrypt.generate_password_hash("admin").decode("utf-8"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper


@app.route("/")
@login_required

def index():
    clients = Client.query.all()
    return render_template("clients.html", clients=clients)


@app.route("/client/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_client():
    if request.method == "POST":
        name = request.form["name"]
        document = request.form["document"]
        client = Client(name=name, document=document)
        db.session.add(client)
        db.session.commit()
        movement = Movement(user_id=session.get("user_id"), client=client, action="create_client", description=f"Cliente {name} creado")
        db.session.add(movement)
        db.session.commit()

        return redirect(url_for("index"))
    return render_template("new_client.html")


@app.route("/client/<int:client_id>")
@login_required

def client_detail(client_id: int):
    client = Client.query.get_or_404(client_id)
    return render_template("client_detail.html", client=client)


@app.route("/client/<int:client_id>/debts", methods=["POST"])
@login_required
@admin_required
def add_debt(client_id: int):
    client = Client.query.get_or_404(client_id)
    amount = float(request.form["amount"])
    description = request.form["description"]
    date_str = request.form.get("date")
    d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    debt = Debt(client=client, amount=amount, description=description, date=d)
    db.session.add(debt)
    movement = Movement(user_id=session.get("user_id"), client=client, action="add_debt", amount=amount, description=description)
    db.session.add(movement)

    db.session.commit()
    return redirect(url_for("client_detail", client_id=client.id))


@app.route("/client/<int:client_id>/payments", methods=["POST"])
@login_required
@admin_required
def add_payment(client_id: int):
    client = Client.query.get_or_404(client_id)
    amount = float(request.form["amount"])
    date_str = request.form.get("date")
    d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    payment = Payment(client=client, amount=amount, date=d)
    db.session.add(payment)
    movement = Movement(user_id=session.get("user_id"), client=client, action="add_payment", amount=amount)
    db.session.add(movement)
    db.session.commit()
    return redirect(url_for("client_detail", client_id=client.id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            return redirect(url_for("index"))
        return render_template("login.html", error="Credenciales inválidas")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Usuario ya existe")
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, password_hash=pw_hash, role="user")
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.run(debug=True)
