from dataclasses import dataclass


@dataclass(slots=True)
class PlanSummary:
    plan_id: int
    name: str