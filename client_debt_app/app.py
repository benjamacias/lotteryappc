import os
from datetime import date, datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from sqlalchemy import inspect, text
from models import db, Client, Debt, Payment, User, Movement
from forms import (
    LoginForm,
    ClientForm,
    DebtForm,
    DebtClientForm,
    PaymentForm,
    WithdrawalForm,
    IncomeForm,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")
csrf = CSRFProtect(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "clients.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = False
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

    inspector = inspect(db.engine)
    if "payment" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("payment")]
        if "method" not in columns:
            db.session.execute(
                text(
                    "ALTER TABLE payment ADD COLUMN method VARCHAR(20) NOT NULL DEFAULT 'cash'"
                )
            )
            db.session.commit()

    if "user" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("user")]
        if "role" not in columns:
            db.session.execute(
                text(
                    "ALTER TABLE user ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"
                )
            )
            db.session.commit()

    if "movement" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("movement")]
        if "user_id" not in columns:
            db.session.execute(
                text(
                    "ALTER TABLE movement ADD COLUMN user_id INTEGER REFERENCES user(id)"
                )
            )
            db.session.commit()

    if not User.query.first():
        admin = User(
            username="admin",
            password_hash=generate_password_hash("admin"),
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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        q = request.form.get("q", "")
        return redirect(url_for("index", q=q))

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
        payment = Payment(
            client=client,
            amount=form.amount.data,
            date=form.date.data,
            method=form.method.data,
        )
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


@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
    user = User.query.get(session.get("user_id"))
    withdraw_form = WithdrawalForm(prefix="withdraw")
    income_form = IncomeForm(prefix="income")
    if withdraw_form.submit.data and withdraw_form.validate_on_submit():
        movement = Movement(
            user_id=user.id,
            action="cash_withdrawal",
            amount=withdraw_form.amount.data,
            description=withdraw_form.description.data,
        )
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for("cash"))
    if income_form.submit.data and income_form.validate_on_submit():
        if user.role != "admin":
            return redirect(url_for("cash"))
        movement = Movement(
            user_id=user.id,
            action="cash_income",
            amount=income_form.amount.data,
            description=income_form.description.data,
        )
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for("cash"))

    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected_date = date.today()

    payments = Payment.query.filter(Payment.date == selected_date).all()
    withdrawals_all = Movement.query.filter_by(action="cash_withdrawal").all()
    withdrawals = [w for w in withdrawals_all if w.timestamp.date() == selected_date]
    incomes_all = Movement.query.filter_by(action="cash_income").all()
    incomes = [i for i in incomes_all if i.timestamp.date() == selected_date]

    total_payments = sum(p.amount for p in payments if p.method == "cash")
    total_incomes = sum(i.amount for i in incomes)
    total_withdrawals = sum(w.amount for w in withdrawals)
    cash_total = total_payments + total_incomes - total_withdrawals

    return render_template(
        "cash.html",
        payments=payments,
        withdrawals=withdrawals,
        incomes=incomes,
        withdraw_form=withdraw_form,
        income_form=income_form,
        date=selected_date,
        total_payments=total_payments,
        total_withdrawals=total_withdrawals,
        total_incomes=total_incomes,
        cash_total=cash_total,
        is_admin=user.role == "admin",
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


@app.route("/deudas/nueva", methods=["GET", "POST"])
@login_required
@admin_required
def new_debt():
    form = DebtClientForm()
    form.client_id.choices = [(c.id, c.name) for c in Client.query.all()]
    if form.validate_on_submit():
        client = Client.query.get_or_404(form.client_id.data)
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
        return redirect(url_for("debts"))
    return render_template("new_debt.html", form=form)


@app.route("/deudas")
@login_required
def debts():
    debts = Debt.query.order_by(Debt.date.desc()).all()
    return render_template("debts.html", debts=debts)


@app.route("/graficos")
@login_required
def charts():
    clients = Client.query.all()
    labels = [c.name for c in clients]
    debts_data = [c.total_debt for c in clients]
    return render_template("charts.html", labels=labels, debts=debts_data)


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
        pw_hash = generate_password_hash(password)
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
