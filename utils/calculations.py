from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import ClassVar, Dict, List


@dataclass
class LineItem:
    category: str
    item_id: str
    item_name: str
    unit: str
    quantity: float
    base_rate: float
    lead_distance: float = 0.0
    lift_height: float = 0.0
    seignorage_percent: float = 0.0
    wastage_percent: float = 0.0
    remarks: str = ""

    LEAD_RATE_PER_KM: ClassVar[float] = 0.005  # 0.5% per km
    LIFT_RATE_PER_METER: ClassVar[float] = 0.003  # 0.3% per meter

    def base_amount(self) -> float:
        return self.quantity * self.base_rate

    def lead_amount(self) -> float:
        return self.base_amount() * self.LEAD_RATE_PER_KM * self.lead_distance

    def lift_amount(self) -> float:
        return self.base_amount() * self.LIFT_RATE_PER_METER * self.lift_height

    def seignorage_amount(self) -> float:
        return self.base_amount() * (self.seignorage_percent / 100.0)

    def wastage_amount(self) -> float:
        return self.base_amount() * (self.wastage_percent / 100.0)

    def total_amount(self) -> float:
        return (
            self.base_amount()
            + self.lead_amount()
            + self.lift_amount()
            + self.seignorage_amount()
            + self.wastage_amount()
        )

    def as_dict(self) -> Dict[str, float | str]:
        data = asdict(self)
        data.update(
            {
                "base_amount": self.base_amount(),
                "lead_amount": self.lead_amount(),
                "lift_amount": self.lift_amount(),
                "seignorage_amount": self.seignorage_amount(),
                "wastage_amount": self.wastage_amount(),
                "total_amount": self.total_amount(),
            }
        )
        return data

    def storage_dict(self) -> Dict[str, float | str]:
        return {
            "category": self.category,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "unit": self.unit,
            "quantity": self.quantity,
            "base_rate": self.base_rate,
            "lead_distance": self.lead_distance,
            "lift_height": self.lift_height,
            "seignorage_percent": self.seignorage_percent,
            "wastage_percent": self.wastage_percent,
            "remarks": self.remarks,
        }


def summarise(items: List[LineItem]) -> Dict[str, float]:
    subtotal = sum(item.base_amount() for item in items)
    lead_total = sum(item.lead_amount() for item in items)
    lift_total = sum(item.lift_amount() for item in items)
    seignorage_total = sum(item.seignorage_amount() for item in items)
    wastage_total = sum(item.wastage_amount() for item in items)
    grand_total = sum(item.total_amount() for item in items)

    return {
        "subtotal": subtotal,
        "lead_total": lead_total,
        "lift_total": lift_total,
        "seignorage_total": seignorage_total,
        "wastage_total": wastage_total,
        "grand_total": grand_total,
    }
