from src.manager import Manager
from src.models import Parameters


def test_functional_total_due_matches_sum_of_tenants():
    manager = Manager(Parameters())

    settlement = manager.get_settlement("apart-polanka", 2025, 1)
    tenants_settlements = manager.create_tenants_settlements(settlement)

    apartment_total = settlement.total_due_pln
    tenants_total = sum(ts.total_due_pln for ts in tenants_settlements)

    assert apartment_total == tenants_total
