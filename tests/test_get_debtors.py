from src.manager import Manager
from src.models import Parameters

def test_get_debtors():
    manager = Manager(Parameters())

    debtors = manager.get_debtors("apart-polanka", 2025, 1)

    assert set(debtors) == {"Jan Nowak", "Adam Kowalski", "Ewa Adamska"}