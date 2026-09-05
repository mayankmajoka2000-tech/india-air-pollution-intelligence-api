from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/policy",
    tags=["Policy"]
)


class Policy(BaseModel):
    baseline_emission: float = Field(gt=0)
    measures: list[dict]


class PolicyPortfolio(BaseModel):
    baseline_emission: float = Field(gt=0)
    budget: float = Field(gt=0)
    measures: list[dict]


@router.post("/simulate")
def simulate(x: Policy):
    scenarios = []

    for m in x.measures:
        reduction_pct = float(m.get("reduction_pct", 0))
        cost = float(m.get("cost", 0))

        reduction_pct = max(0, min(reduction_pct, 100))

        reduction_amount = (
            x.baseline_emission
            * reduction_pct
            / 100
        )

        net_emission = (
            x.baseline_emission
            - reduction_amount
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


@router.post("/portfolio")
def portfolio(x: PolicyPortfolio):
    """
    Select a combination of policy measures within
    the available budget.

    The optimizer uses a greedy cost-effectiveness
    approach: measures with the lowest cost per unit
    emission reduction are selected first.
    """

    candidates = []

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

        cost = max(0, cost)

        reduction_amount = (
            x.baseline_emission
            * reduction_pct
            / 100
        )

        if reduction_amount <= 0 or cost <= 0:
            continue

        cost_per_unit = (
            cost / reduction_amount
        )

        candidates.append({
            "measure": name,
            "reduction_pct": round(
                reduction_pct, 2
            ),
            "emission_reduction": reduction_amount,
            "investment_cost": cost,
            "cost_per_unit_reduction": cost_per_unit
        })

    # Lowest cost per unit reduction = highest priority
    candidates.sort(
        key=lambda x: x["cost_per_unit_reduction"]
    )

    selected = []
    remaining_budget = x.budget
    total_reduction = 0
    total_cost = 0

    for item in candidates:

        if item["investment_cost"] <= remaining_budget:

            selected.append({
                "measure": item["measure"],
                "reduction_pct": item["reduction_pct"],
                "emission_reduction": round(
                    item["emission_reduction"], 2
                ),
                "investment_cost": round(
                    item["investment_cost"], 2
                ),
                "cost_per_unit_reduction": round(
                    item["cost_per_unit_reduction"], 4
                )
            })

            total_reduction += (
                item["emission_reduction"]
            )

            total_cost += (
                item["investment_cost"]
            )

            remaining_budget -= (
                item["investment_cost"]
            )

    net_emission = (
        x.baseline_emission
        - total_reduction
    )

    total_reduction_pct = (
        total_reduction
        / x.baseline_emission
        * 100
    )

    return {
        "status": "success",
        "objective": (
            "maximize pollution reduction "
            "within available budget"
        ),
        "baseline_emission": round(
            x.baseline_emission, 2
        ),
        "available_budget": round(
            x.budget, 2
        ),
        "budget_used": round(
            total_cost, 2
        ),
        "remaining_budget": round(
            remaining_budget, 2
        ),
        "total_emission_reduction": round(
            total_reduction, 2
        ),
        "total_reduction_pct": round(
            total_reduction_pct, 2
        ),
        "estimated_net_emission": round(
            net_emission, 2
        ),
        "selected_measures": selected,
        "selection_count": len(selected),
        "selection_method": (
            "Greedy selection based on lowest "
            "cost per unit emission reduction"
        ),
        "decision_note": (
            "This is a scenario-based budget allocation "
            "tool. It assumes the stated reduction and "
            "investment estimates are independent and "
            "additive. It is not a formal linear-programming "
            "or mixed-integer optimization model."
        )
    }
