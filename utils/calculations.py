from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar, Dict, List, Optional


@dataclass
class Component:
    group: str
    description: str
    unit: str
    quantity: float
    rate: float

    def amount(self) -> float:
        return self.quantity * self.rate

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group": self.group,
            "description": self.description,
            "unit": self.unit,
            "quantity": self.quantity,
            "rate": self.rate,
            "amount": self.amount(),
        }


@dataclass
class Adjustment:
    label: str
    base_stage: str
    percent: Optional[float] = None
    factor: Optional[float] = None
    amount: Optional[float] = None
    result_stage: Optional[str] = None
    notes: Optional[str] = None

    def compute_amount(self, base_value: float) -> float:
        if self.amount is not None:
            return self.amount
        if self.percent is not None:
            return base_value * (self.percent / 100.0)
        if self.factor is not None:
            return base_value * self.factor
        raise ValueError(
            f"Adjustment '{self.label}' must define amount, percent, or factor."
        )

    def to_dict(self, base_value: float, amount: float, result_value: float) -> Dict[str, Any]:
        return {
            "label": self.label,
            "base_stage": self.base_stage,
            "base_value": base_value,
            "amount": amount,
            "result_stage": self.result_stage,
            "result_value": result_value,
            "notes": self.notes,
        }


@dataclass
class CompositeBreakdown:
    components: List[Component]
    adjustments: List[Adjustment]
    output_quantity: float
    round_to: Optional[int] = None
    say_total: Optional[float] = None

    def __post_init__(self) -> None:
        if self.output_quantity <= 0:
            raise ValueError("Output quantity must be greater than zero")

    def base_total(self) -> float:
        return sum(component.amount() for component in self.components)

    def compute(self) -> Dict[str, Any]:
        stages: Dict[str, float] = {"X": self.base_total()}
        breakdown_components = [component.to_dict() for component in self.components]
        adjustment_rows: List[Dict[str, Any]] = []

        running_total = stages["X"]
        for adjustment in self.adjustments:
            base_value = stages.get(adjustment.base_stage)
            if base_value is None:
                raise KeyError(
                    f"Stage '{adjustment.base_stage}' not defined before applying '{adjustment.label}'"
                )
            amount = adjustment.compute_amount(base_value)
            result_value = base_value + amount
            if adjustment.result_stage:
                stages[adjustment.result_stage] = result_value
                running_total = result_value
            else:
                running_total += amount
            adjustment_rows.append(
                adjustment.to_dict(base_value=base_value, amount=amount, result_value=result_value)
            )

        raw_total = running_total
        final_total = raw_total
        if self.round_to is not None:
            final_total = round(final_total, self.round_to)
        if self.say_total is not None:
            final_total = self.say_total

        unit_rate = final_total / self.output_quantity

        return {
            "components": breakdown_components,
            "adjustments": adjustment_rows,
            "stages": stages,
            "base_total": stages["X"],
            "raw_total": raw_total,
            "final_total": final_total,
            "unit_rate": unit_rate,
            "output_quantity": self.output_quantity,
        }


@dataclass
class CompositeItem:
    id: str
    name: str
    unit: str
    components: List[Component]
    adjustments: List[Adjustment]
    output_quantity: float = 1.0
    round_to: Optional[int] = None
    say_total: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "CompositeItem":
        components = [Component(**component) for component in payload.get("components", [])]
        adjustments = [Adjustment(**adjustment) for adjustment in payload.get("adjustments", [])]
        return cls(
            id=payload.get("id", ""),
            name=payload.get("name", ""),
            unit=payload.get("unit", ""),
            components=components,
            adjustments=adjustments,
            output_quantity=payload.get("output_quantity", 1.0),
            round_to=payload.get("round_to"),
            say_total=payload.get("say_total"),
            metadata={key: value for key, value in payload.items() if key not in {
                "components",
                "adjustments",
                "output_quantity",
                "round_to",
                "say_total",
            }},
        )

    def breakdown(self) -> Dict[str, Any]:
        composite_breakdown = CompositeBreakdown(
            components=self.components,
            adjustments=self.adjustments,
            output_quantity=self.output_quantity,
            round_to=self.round_to,
            say_total=self.say_total,
        )
        data = composite_breakdown.compute()
        if self.metadata:
            data["metadata"] = self.metadata
        data["item_id"] = self.id
        data["item_name"] = self.name
        data["unit"] = self.unit
        return data

    def unit_rate(self) -> float:
        return self.breakdown()["unit_rate"]


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
    metadata: Dict[str, Any] = field(default_factory=dict)

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
            "metadata": self.metadata,
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
