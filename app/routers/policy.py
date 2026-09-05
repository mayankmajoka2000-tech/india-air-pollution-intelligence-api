from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/policy",
    tags=["Policy"]
)


class Policy(BaseModel):
    baseline_emission: float = Field(gt=0)
    measures: list[dict]


@router.post("/simulate")
def simulate(x: Policy):
    scenarios = []

    for m in x.measures:
        reduction_pct = float(m.get("reduction_pct", 0))
        cost = float(m.get("cost", 0))

        reduction_pct = max(0, min(reduction_pct, 100))
        reduction_amount = (
            x.baseline_emission * reduction_pct / 100
        )

        net_emission = (
            x.baseline_emission - reduction_amount
        )

        cost_per_unit = (
            cost / reduction_amount
            if reduction_amount > 0
            else None
        )

        scenarios.append({
            "measure": m.get("name", "unnamed"),
            "reduction_pct": round(reduction_pct, 2),
            "baseline_emission": round(
                x.baseline_emission, 2
            ),
            "emission_reduction": round(
                reduction_amount, 2
            ),
            "net_emission": round(
                net_emission, 2
            ),
            "investment_cost": round(
                cost, 2
            ),
            "cost_per_unit_reduction": (
                round(cost_per_unit, 4)
                if cost_per_unit is not None
                else None
            )
        })

    return {
        "status": "success",
        "baseline_emission": round(
            x.baseline_emission, 2
        ),
        "scenario_count": len(scenarios),
        "scenarios": scenarios
    }


@router.post("/optimize")
def optimize(x: Policy):
    ranked = []

    for m in x.measures:
        name = m.get("name", "unnamed")

        reduction_pct = float(
            m.get("reduction_pct", 0)
        )

        cost = float(
            m.get("cost", 0)
        )

        reduction_pct = max(
            0,
            min(reduction_pct, 100)
        )

        reduction_amount = (
            x.baseline_emission
            * reduction_pct
            / 100
        )

        net_emission = (
            x.baseline_emission
            - reduction_amount
        )

        if reduction_amount > 0:
            cost_per_unit = (
                cost / reduction_amount
            )
        else:
            cost_per_unit = None

        # Cost-effectiveness score:
        # higher = better
        if cost_per_unit and cost_per_unit > 0:
            score = 1 / cost_per_unit
        else:
            score = 0

        ranked.append({
            "measure": name,
            "reduction_pct": round(
                reduction_pct, 2
            ),
            "emission_reduction": round(
                reduction_amount, 2
            ),
            "net_emission": round(
                net_emission, 2
            ),
            "investment_cost": round(
                cost, 2
            ),
            "cost_per_unit_reduction": (
                round(cost_per_unit, 4)
                if cost_per_unit is not None
                else None
            ),
            "cost_effectiveness_score": round(
                score, 6
            )
        })

    # Best intervention = lowest cost per unit reduction
    ranked.sort(
        key=lambda x: (
            x["cost_per_unit_reduction"]
            if x["cost_per_unit_reduction"] is not None
            else float("inf")
        )
    )

    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank

    return {
        "status": "success",
        "objective": (
            "maximize pollution reduction "
            "per unit investment"
        ),
        "baseline_emission": round(
            x.baseline_emission, 2
        ),
        "recommended_measure": (
            ranked[0]["measure"]
            if ranked
            else None
        ),
        "ranking": ranked,
        "decision_note": (
            "Lower cost per unit reduction indicates "
            "greater cost-effectiveness. Results are "
            "scenario-based and depend on the assumptions "
            "provided for reduction percentage and cost."
        )
    }
