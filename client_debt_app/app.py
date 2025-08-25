import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Client, Debt, Payment, User, Movement

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "clients.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(username="admin", password_hash=generate_password_hash("admin"))
        db.session.add(admin)
        db.session.commit()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


@app.route("/")
@login_required

def index():
    q = request.args.get("q", "")
    if q:
        clients = Client.query.filter(Client.name.ilike(f"%{q}%")).all()
    else:
        clients = Client.query.all()
    return render_template("clients.html", clients=clients, q=q)


@app.route("/client/new", methods=["GET", "POST"])
@login_required

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


@app.route("/report")
@login_required
def report():
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    client_id = request.args.get("client_id")

    query = Movement.query
    start_date = None
    end_date = None
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        query = query.filter(Movement.timestamp >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        query = query.filter(Movement.timestamp <= end_date)
    if client_id:
        query = query.filter(Movement.client_id == int(client_id))

    movements = query.order_by(Movement.timestamp.desc()).all()
    total_debt = sum(m.amount or 0 for m in movements if m.action == "add_debt")
    total_payment = sum(m.amount or 0 for m in movements if m.action == "add_payment")

    clients = Client.query.all()
    return render_template(
        "report.html",
        movements=movements,
        clients=clients,
        start_date=start_date_str,
        end_date=end_date_str,
        client_id=client_id,
        total_debt=total_debt,
        total_payment=total_payment,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            return redirect(url_for("index"))
        return render_template("login.html", error="Credenciales inválidas")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.run(debug=True)
