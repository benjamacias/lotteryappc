import pytest
from app import app, db, User
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(username="admin", password_hash=generate_password_hash("admin"))
        db.session.add(admin)
        db.session.commit()
        with app.test_client() as client:
            yield client


def test_index_requires_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_success(client):
    response = client.post(
        "/login", data={"username": "admin", "password": "admin"}, follow_redirects=True
    )
    assert b"Clientes" in response.data
