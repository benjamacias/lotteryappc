import pytest
from app import app, db, Client, Debt, Payment


@pytest.fixture
def app_context():
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield


def test_total_debt(app_context):
    client = Client(name="John Doe", document="123")
    db.session.add(client)
    db.session.commit()
    debt1 = Debt(client=client, amount=100.0, description="d1")
    debt2 = Debt(client=client, amount=50.0, description="d2")
    payment = Payment(client=client, amount=80.0)
    db.session.add_all([debt1, debt2, payment])
    db.session.commit()
    assert client.total_debt == 70.0
