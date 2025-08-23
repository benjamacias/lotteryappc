from flask import Flask, render_template, abort
from data import clients

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("clients.html", clients=clients)

@app.route("/client/<int:client_id>")
def client_detail(client_id: int):
    client = next((c for c in clients if c.id == client_id), None)
    if client is None:
        abort(404)
    return render_template("client_detail.html", client=client)

if __name__ == "__main__":
    app.run(debug=True)
