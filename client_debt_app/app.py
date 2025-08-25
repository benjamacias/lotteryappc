import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from models import db, Client, Debt, Payment, User, Movement
from forms import LoginForm, ClientForm, DebtForm, PaymentForm

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")
csrf = CSRFProtect(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "clients.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

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
    q = request.args.get("q", "")
    if q:
        clients = Client.query.filter(Client.name.ilike(f"%{q}%")).all()
    else:
        clients = Client.query.all()
    return render_template("clients.html", clients=clients, q=q)


@app.route("/client/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_client():
    form = ClientForm()
    if form.validate_on_submit():
        client = Client(name=form.name.data, document=form.document.data)
        db.session.add(client)
        db.session.commit()
        movement = Movement(
            user_id=session.get("user_id"),
            client=client,
            action="create_client",
            description=f"Cliente {form.name.data} creado",
        )
        db.session.add(movement)
        db.session.commit()

        return redirect(url_for("index"))
    return render_template("new_client.html", form=form)


@app.route("/client/<int:client_id>")
@login_required

def client_detail(client_id: int):
    client = Client.query.get_or_404(client_id)
    debt_form = DebtForm()
    payment_form = PaymentForm()
    return render_template(
        "client_detail.html", client=client, debt_form=debt_form, payment_form=payment_form
    )


@app.route("/client/<int:client_id>/debts", methods=["POST"])
@login_required
@admin_required
def add_debt(client_id: int):
    client = Client.query.get_or_404(client_id)
    form = DebtForm()
    if form.validate_on_submit():
        debt = Debt(
            client=client,
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data or date.today(),
        )
        db.session.add(debt)
        movement = Movement(
            user_id=session.get("user_id"),
            client=client,
            action="add_debt",
            amount=form.amount.data,
            description=form.description.data,
        )
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for("client_detail", client_id=client.id))
    payment_form = PaymentForm()
    return render_template(
        "client_detail.html", client=client, debt_form=form, payment_form=payment_form
    )


@app.route("/client/<int:client_id>/payments", methods=["POST"])
@login_required
@admin_required
def add_payment(client_id: int):
    client = Client.query.get_or_404(client_id)
    form = PaymentForm()
    if form.validate_on_submit():
        payment = Payment(client=client, amount=form.amount.data, date=form.date.data)
        db.session.add(payment)
        movement = Movement(
            user_id=session.get("user_id"),
            client=client,
            action="add_payment",
            amount=form.amount.data,
        )
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for("client_detail", client_id=client.id))
    debt_form = DebtForm()
    return render_template(
        "client_detail.html", client=client, debt_form=debt_form, payment_form=form
    )


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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session["user_id"] = user.id
            return redirect(url_for("index"))
        return render_template("login.html", form=form, error="Credenciales inválidas")
    return render_template("login.html", form=form)


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
