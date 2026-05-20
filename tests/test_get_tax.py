from src.manager import Manager
from src.models import Parameters

def test_get_tax():
    manager = Manager(Parameters())

    tax = manager.get_tax(2025, 1, 0.085)

    assert tax == round(7500 * 0.085)
