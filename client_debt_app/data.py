from dataclasses import dataclass, field
from datetime import date
from typing import List

@dataclass
class Debt:
    date: date
    amount: float
    description: str

@dataclass
class Client:
    id: int
    name: str
    document: str
    debts: List[Debt] = field(default_factory=list)

    @property
    def total_debt(self) -> float:
        return sum(d.amount for d in self.debts)

clients: List[Client] = [
    Client(
        id=1,
        name="Juan Pérez",
        document="12345678",
        debts=[
            Debt(date(2024, 1, 5), 1500.0, "Compra de mercadería"),
            Debt(date(2024, 2, 10), 2000.0, "Préstamo"),
        ],
    ),
    Client(
        id=2,
        name="María Gómez",
        document="87654321",
        debts=[
            Debt(date(2024, 3, 1), 500.0, "Servicio de internet"),
        ],
    ),
]
