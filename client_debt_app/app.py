import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for
from models import db, Client, Debt, Payment

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "clients.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    clients = Client.query.all()
    return render_template("clients.html", clients=clients)


@app.route("/client/new", methods=["GET", "POST"])
def new_client():
    if request.method == "POST":
        name = request.form["name"]
        document = request.form["document"]
        client = Client(name=name, document=document)
        db.session.add(client)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("new_client.html")


@app.route("/client/<int:client_id>")
def client_detail(client_id: int):
    client = Client.query.get_or_404(client_id)
    return render_template("client_detail.html", client=client)


@app.route("/client/<int:client_id>/debts", methods=["POST"])
def add_debt(client_id: int):
    client = Client.query.get_or_404(client_id)
    amount = float(request.form["amount"])
    description = request.form["description"]
    date_str = request.form.get("date")
    d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    debt = Debt(client=client, amount=amount, description=description, date=d)
    db.session.add(debt)
    db.session.commit()
    return redirect(url_for("client_detail", client_id=client.id))


@app.route("/client/<int:client_id>/payments", methods=["POST"])
def add_payment(client_id: int):
    client = Client.query.get_or_404(client_id)
    amount = float(request.form["amount"])
    date_str = request.form.get("date")
    d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    payment = Payment(client=client, amount=amount, date=d)
    db.session.add(payment)
    db.session.commit()
    return redirect(url_for("client_detail", client_id=client.id))

if __name__ == "__main__":
    app.run(debug=True)
