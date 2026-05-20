from src.models import Apartment, Bill, Parameters, Tenant, TenantSettlement, Transfer, ApartmentSettlement
from typing import List, Tuple

class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None) -> float | None:
        if month is not None and (month < 1 or month > 12):
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key and (year is None or bill.settlement_year == year) and (month is None or bill.settlement_month == month):
                total_cost += bill.amount_pln
        return total_cost

    def get_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = self.get_apartment_costs(apartment_key, year, month)
        if total_cost is None:
            return None

        settlement = ApartmentSettlement(
            key=f"{apartment_key}-{year}-{month}",
            apartment=apartment_key,
            year=year,
            month=month,
            total_due_pln=total_cost
        )

        settlement.total_transfers_pln = self.get_apartment_transfers(apartment_key, year, month)

        settlement.balance_pln = settlement.total_transfers_pln - settlement.total_due_pln
        return settlement
    
    def create_tenants_settlements(self, apartment_settlement: ApartmentSettlement) -> List[TenantSettlement] | None:
        if apartment_settlement.month < 1 or apartment_settlement.month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_settlement.apartment not in self.apartments:
            return None

        tenants_in_apartment = [
            (tenant_key, tenant)
            for tenant_key, tenant in self.tenants.items()
            if tenant.apartment == apartment_settlement.apartment
        ]

        if not tenants_in_apartment:
            return []

        per_tenant_due = apartment_settlement.total_due_pln / len(tenants_in_apartment)
        settlements = []

        for tenant_key, tenant in tenants_in_apartment:
            ts = TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=apartment_settlement.key,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                total_due_pln=per_tenant_due
            )

            ts.total_transfers_pln = self.get_tenant_transfers(
                tenant_key,
                apartment_settlement.year,
                apartment_settlement.month
            )
            ts.balance_pln = ts.total_transfers_pln - ts.total_due_pln
            settlements.append(ts)
        return settlements
 
    
    def get_apartment_transfers(self, apartment_key: str, year: int, month: int) -> float:
        total = 0.0
        for transfer in self.transfers:
            tenant = self.tenants.get(transfer.tenant)
            if tenant and tenant.apartment == apartment_key:
                if transfer.settlement_year == year and transfer.settlement_month == month:
                    total += transfer.amount_pln
        return total
    
    def get_tenant_transfers(self, tenant_key: str, year: int, month: int) -> float:
        return sum(
            t.amount_pln
            for t in self.transfers
            if t.tenant == tenant_key == year
            and t.settlement_year == year
            and t.settlement_month == month    
        )
    
    
    def get_debtors(self, apartment_key: str, year: int, month: int) -> list[str]:
        debtors = []

        for tenant_key, tenant in self.tenants.items():
            if tenant.apartment != apartment_key:
                continue

            transfers = self.get_tenant_transfers(tenant_key, year, month)
            rent = tenant.rent_pln

            if transfers < rent:
                debtors.append(tenant.name)

        return debtors

