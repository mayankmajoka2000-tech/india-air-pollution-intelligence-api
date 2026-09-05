from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/msme",
    tags=["MSME"]
)


# ============================================================
# MSME INPUT MODEL
# ============================================================

class MSME(BaseModel):
    sector: str
    fuel_consumption: float = Field(ge=0)
    electricity_kwh: float = Field(ge=0)
    annual_output: float = Field(gt=0)


# ============================================================
# TRANSITION SCENARIO INPUT MODEL
# ============================================================

class TransitionScenario(BaseModel):
    sector: str
    fuel_consumption: float = Field(ge=0)
    electricity_kwh: float = Field(ge=0)
    annual_output: float = Field(gt=0)

    financing_amount: float = Field(gt=0)

    fuel_reduction_pct: float = Field(
        ge=0,
        le=100,
        default=0
    )

    electricity_reduction_pct: float = Field(
        ge=0,
        le=100,
        default=0
    )


# ============================================================
# AIR POLLUTION SCREENING INPUT MODEL
# ============================================================

class AirPollutionAssessment(BaseModel):
    sector: str

    fuel_consumption: float = Field(ge=0)
    electricity_kwh: float = Field(ge=0)
    annual_output: float = Field(gt=0)

    pm25: float = Field(ge=0)
    pm10: float = Field(ge=0)
    no2: float = Field(ge=0)
    so2: float = Field(ge=0)
    co: float = Field(ge=0)


# ============================================================
# SECTOR BENCHMARKS
# ============================================================

SECTOR_BENCHMARKS = {

    "manufacturing": {
        "emission_intensity": 2.0
    },

    "textile": {
        "emission_intensity": 1.8
    },

    "food processing": {
        "emission_intensity": 1.5
    },

    "chemical": {
        "emission_intensity": 2.5
    },

    "cement": {
        "emission_intensity": 3.0
    },

    "metal": {
        "emission_intensity": 2.8
    },

    "automotive": {
        "emission_intensity": 2.2
    },

    "pharmaceutical": {
        "emission_intensity": 1.6
    },

    "default": {
        "emission_intensity": 2.0
    }
}


# ============================================================
# POLLUTANT SCREENING THRESHOLDS
# ============================================================

# Screening thresholds for API development.
# These are NOT official regulatory limits.

POLLUTANT_THRESHOLDS = {
    "PM2.5": 60.0,
    "PM10": 100.0,
    "NO2": 80.0,
    "SO2": 80.0,
    "CO": 2.0
}


# ============================================================
# EMISSION CALCULATION
# ============================================================

def calculate_emissions(x: MSME):

    fuel_co2e = (
        x.fuel_consumption * 2.75
    )

    electricity_co2e = (
        x.electricity_kwh * 0.70
    )

    total_co2e = (
        fuel_co2e
        + electricity_co2e
    )

    intensity = (
        total_co2e
        / x.annual_output
    )

    return {
        "fuel_co2e": fuel_co2e,
        "electricity_co2e": electricity_co2e,
        "total_co2e": total_co2e,
        "intensity": intensity
    }


# ============================================================
# SECTOR BENCHMARK FUNCTION
# ============================================================

def get_sector_benchmark(sector: str):

    sector_key = sector.strip().lower()

    benchmark = SECTOR_BENCHMARKS.get(
        sector_key,
        SECTOR_BENCHMARKS["default"]
    )

    if sector_key in SECTOR_BENCHMARKS:

        benchmark_source = (
            "sector-specific development benchmark"
        )

    else:

        benchmark_source = (
            "default development benchmark"
        )

    return (
        benchmark["emission_intensity"],
        benchmark_source
    )


# ============================================================
# MSME ASSESSMENT
# ============================================================

@router.post("/assessment")
def assessment(x: MSME):

    emissions = calculate_emissions(x)

    total = emissions["total_co2e"]

    return {

        "status": "success",

        "sector": x.sector,

        "estimated_co2e": round(
            total,
            2
        ),

        "emission_intensity": round(
            emissions["intensity"],
            4
        ),

        "fuel_co2e": round(
            emissions["fuel_co2e"],
            2
        ),

        "electricity_co2e": round(
            emissions["electricity_co2e"],
            2
        ),

        "priority": (
            "High"
            if total > 100000
            else "Standard"
        ),

        "method": (
            "Estimated CO2e from fuel consumption "
            "and electricity consumption"
        ),

        "interpretation_note": (
            "This is a screening-level estimate "
            "based on the emission factors supplied "
            "to the model. It is not a verified "
            "greenhouse-gas inventory."
        )
    }


# ============================================================
# GREEN FINANCE SCREENING
# ============================================================

@router.post("/green-finance-screening")
def finance(x: MSME):

    emissions = calculate_emissions(x)

    total = emissions["total_co2e"]

    intensity = emissions["intensity"]

    # --------------------------------------------------------
    # ABSOLUTE EMISSION SCORE
    # --------------------------------------------------------

    emission_score = max(
        0,
        100 - (total / 10000)
    )

    # --------------------------------------------------------
    # INTENSITY SCORE
    # --------------------------------------------------------

    intensity_score = max(
        0,
        100 - (intensity * 10)
    )

    # --------------------------------------------------------
    # SECTOR BENCHMARK
    # --------------------------------------------------------

    benchmark, benchmark_source = (
        get_sector_benchmark(x.sector)
    )

    benchmark_ratio = (
        intensity / benchmark
        if benchmark > 0
        else None
    )

    # --------------------------------------------------------
    # BENCHMARK PERFORMANCE
    # --------------------------------------------------------

    if benchmark_ratio is not None:

        if benchmark_ratio <= 0.75:

            benchmark_performance = (
                "Better than benchmark"
            )

        elif benchmark_ratio <= 1.00:

            benchmark_performance = (
                "Near benchmark"
            )

        elif benchmark_ratio <= 1.25:

            benchmark_performance = (
                "Above benchmark"
            )

        else:

            benchmark_performance = (
                "Significantly above benchmark"
            )

    else:

        benchmark_performance = (
            "Benchmark unavailable"
        )

    # --------------------------------------------------------
    # BENCHMARK SCORE
    # --------------------------------------------------------

    if benchmark_ratio is not None:

        benchmark_score = max(
            0,
            min(
                100,
                100 - (
                    (benchmark_ratio - 0.75)
                    * 100
                )
            )
        )

    else:

        benchmark_score = 50

    # --------------------------------------------------------
    # COMBINED SCREENING SCORE
    # --------------------------------------------------------

    screening_score = (

        emission_score * 0.40

        + intensity_score * 0.25

        + benchmark_score * 0.35

    )

    screening_score = min(
        100,
        max(
            0,
            screening_score
        )
    )

    # --------------------------------------------------------
    # GREEN FINANCE POTENTIAL
    # --------------------------------------------------------

    if screening_score >= 75:

        eligibility = (
            "High potential"
        )

    elif screening_score >= 50:

        eligibility = (
            "Moderate potential"
        )

    elif screening_score >= 25:

        eligibility = (
            "Low potential"
        )

    else:

        eligibility = (
            "Requires improvement"
        )

    # --------------------------------------------------------
    # DOMINANT EMISSION SOURCE
    # --------------------------------------------------------

    if (
        emissions["fuel_co2e"]
        > emissions["electricity_co2e"]
    ):

        dominant_source = (
            "fuel consumption"
        )

    elif (
        emissions["electricity_co2e"]
        > emissions["fuel_co2e"]
    ):

        dominant_source = (
            "electricity consumption"
        )

    else:

        dominant_source = (
            "balanced"
        )

    # --------------------------------------------------------
    # RECOMMENDED ACTIONS
    # --------------------------------------------------------

    recommended_actions = []

    if emissions["fuel_co2e"] > 0:

        recommended_actions.append(
            "clean fuel transition"
        )

    if emissions["electricity_co2e"] > 0:

        recommended_actions.append(
            "energy efficiency and renewable electricity"
        )

    if benchmark_ratio is not None:

        if benchmark_ratio > 1:

            recommended_actions.append(
                "sector-specific emission intensity reduction"
            )

        if benchmark_ratio > 1.25:

            recommended_actions.append(
                "prepare an emissions-reduction investment plan"
            )

    recommended_actions.extend([
        "emission monitoring",
        "pollution-control equipment",
        "resource efficiency"
    ])

    return {

        "status": "success",

        "sector": x.sector,

        "estimated_co2e": round(
            total,
            2
        ),

        "emission_intensity": round(
            intensity,
            4
        ),

        "fuel_co2e": round(
            emissions["fuel_co2e"],
            2
        ),

        "electricity_co2e": round(
            emissions["electricity_co2e"],
            2
        ),

        "dominant_emission_source": (
            dominant_source
        ),

        "sector_benchmark": round(
            benchmark,
            4
        ),

        "benchmark_ratio": round(
            benchmark_ratio,
            4
        )
        if benchmark_ratio is not None
        else None,

        "benchmark_performance": (
            benchmark_performance
        ),

        "benchmark_source": (
            benchmark_source
        ),

        "emission_score": round(
            emission_score,
            2
        ),

        "intensity_score": round(
            intensity_score,
            2
        ),

        "benchmark_score": round(
            benchmark_score,
            2
        ),

        "screening_score": round(
            screening_score,
            2
        ),

        "green_finance_potential": (
            eligibility
        ),

        "recommended_actions": (
            recommended_actions
        ),

        "scoring_weights": {

            "absolute_emissions": 0.40,

            "emission_intensity": 0.25,

            "sector_benchmark": 0.35

        },

        "method": (
            "Green-finance screening using absolute "
            "emissions, emission intensity and "
            "sector benchmark performance"
        ),

        "important_note": (
            "Sector benchmarks in this API are "
            "development-stage screening assumptions "
            "and are not official regulatory or "
            "lending thresholds. Actual green-finance "
            "decisions should use verified emissions, "
            "sector-specific benchmarks, project "
            "additionality, financial viability, "
            "credit risk and applicable lender or "
            "regulatory criteria."
        )
    }


# ============================================================
# MSME GREEN-FINANCE TRANSITION SCENARIO
# ============================================================

@router.post("/transition-scenario")
def transition_scenario(
    x: TransitionScenario
):

    # --------------------------------------------------------
    # CURRENT EMISSIONS
    # --------------------------------------------------------

    current_fuel_co2e = (
        x.fuel_consumption * 2.75
    )

    current_electricity_co2e = (
        x.electricity_kwh * 0.70
    )

    current_total_co2e = (
        current_fuel_co2e
        + current_electricity_co2e
    )

    # --------------------------------------------------------
    # PROJECTED ENERGY CONSUMPTION
    # --------------------------------------------------------

    future_fuel_consumption = (
        x.fuel_consumption
        * (
            1
            - x.fuel_reduction_pct / 100
        )
    )

    future_electricity_kwh = (
        x.electricity_kwh
        * (
            1
            - x.electricity_reduction_pct / 100
        )
    )

    # --------------------------------------------------------
    # PROJECTED EMISSIONS
    # --------------------------------------------------------

    future_fuel_co2e = (
        future_fuel_consumption * 2.75
    )

    future_electricity_co2e = (
        future_electricity_kwh * 0.70
    )

    future_total_co2e = (
        future_fuel_co2e
        + future_electricity_co2e
    )

    # --------------------------------------------------------
    # ENVIRONMENTAL BENEFIT
    # --------------------------------------------------------

    emission_reduction = (
        current_total_co2e
        - future_total_co2e
    )

    reduction_pct = (
        emission_reduction
        / current_total_co2e
        * 100
        if current_total_co2e > 0
        else 0
    )

    # --------------------------------------------------------
    # EMISSION INTENSITY
    # --------------------------------------------------------

    current_intensity = (
        current_total_co2e
        / x.annual_output
    )

    future_intensity = (
        future_total_co2e
        / x.annual_output
    )

    # --------------------------------------------------------
    # CO2E REDUCTION PER UNIT FINANCE
    # --------------------------------------------------------

    co2e_reduction_per_finance = (
        emission_reduction
        / x.financing_amount
        if x.financing_amount > 0
        else 0
    )

    # --------------------------------------------------------
    # IMPACT CATEGORY
    # --------------------------------------------------------

    if reduction_pct >= 30:

        impact_category = (
            "High environmental impact"
        )

    elif reduction_pct >= 15:

        impact_category = (
            "Moderate environmental impact"
        )

    elif reduction_pct > 0:

        impact_category = (
            "Low environmental impact"
        )

    else:

        impact_category = (
            "No projected emission reduction"
        )

    return {

        "status": "success",

        "sector": x.sector,

        "financing_amount": round(
            x.financing_amount,
            2
        ),

        "baseline": {

            "fuel_consumption": round(
                x.fuel_consumption,
                2
            ),

            "electricity_kwh": round(
                x.electricity_kwh,
                2
            ),

            "estimated_co2e": round(
                current_total_co2e,
                2
            ),

            "emission_intensity": round(
                current_intensity,
                4
            )
        },

        "intervention": {

            "fuel_reduction_pct": round(
                x.fuel_reduction_pct,
                2
            ),

            "electricity_reduction_pct": round(
                x.electricity_reduction_pct,
                2
            )
        },

        "projected": {

            "fuel_consumption": round(
                future_fuel_consumption,
                2
            ),

            "electricity_kwh": round(
                future_electricity_kwh,
                2
            ),

            "estimated_co2e": round(
                future_total_co2e,
                2
            ),

            "emission_intensity": round(
                future_intensity,
                4
            )
        },

        "environmental_impact": {

            "co2e_reduction": round(
                emission_reduction,
                2
            ),

            "reduction_pct": round(
                reduction_pct,
                2
            ),

            "co2e_reduction_per_unit_finance": round(
                co2e_reduction_per_finance,
                6
            ),

            "impact_category": (
                impact_category
            )
        },

        "method": (
            "Scenario-based estimation using assumed "
            "fuel and electricity reduction percentages"
        ),

        "important_note": (
            "This is a screening-level transition scenario. "
            "It assumes the stated reductions are achieved "
            "and does not constitute a verified emissions "
            "reduction, carbon credit calculation, or "
            "formal green-finance impact assessment."
        )
    }


# ============================================================
# MSME AIR POLLUTION ASSESSMENT
# ============================================================

@router.post("/air-pollution-assessment")
def air_pollution_assessment(
    x: AirPollutionAssessment
):

    pollutants = {
        "PM2.5": x.pm25,
        "PM10": x.pm10,
        "NO2": x.no2,
        "SO2": x.so2,
        "CO": x.co
    }

    # --------------------------------------------------------
    # POLLUTANT STATUS
    # --------------------------------------------------------

    pollutant_status = {}

    exceedance_count = 0

    for pollutant, value in pollutants.items():

        threshold = (
            POLLUTANT_THRESHOLDS[pollutant]
        )

        ratio = (
            value / threshold
            if threshold > 0
            else 0
        )

        if ratio <= 0.75:

            status = "Low"

        elif ratio <= 1.00:

            status = "Moderate"

        elif ratio <= 1.25:

            status = "High"

        else:

            status = "Very High"

        if ratio > 1:

            exceedance_count += 1

        pollutant_status[pollutant] = {

            "observed_value": round(
                value,
                2
            ),

            "screening_threshold": round(
                threshold,
                2
            ),

            "threshold_ratio": round(
                ratio,
                2
            ),

            "status": status
        }

    # --------------------------------------------------------
    # POLLUTION PRESSURE SCORE
    # --------------------------------------------------------

    ratios = []

    for pollutant, value in pollutants.items():

        threshold = (
            POLLUTANT_THRESHOLDS[pollutant]
        )

        if threshold > 0:

            ratios.append(
                value / threshold
            )

    average_ratio = (
        sum(ratios) / len(ratios)
        if ratios
        else 0
    )

    pollution_pressure_score = min(
        100,
        average_ratio * 100
    )

    # --------------------------------------------------------
    # OVERALL POLLUTION RISK
    # --------------------------------------------------------

    if pollution_pressure_score >= 125:

        pollution_risk = "Very High"

    elif pollution_pressure_score >= 100:

        pollution_risk = "High"

    elif pollution_pressure_score >= 75:

        pollution_risk = "Moderate"

    else:

        pollution_risk = "Low"

    # --------------------------------------------------------
    # PRIORITY POLLUTANTS
    # --------------------------------------------------------

    priority_pollutants = sorted(
        pollutants.keys(),
        key=lambda p: (
            pollutants[p]
            / POLLUTANT_THRESHOLDS[p]
        ),
        reverse=True
    )

    priority_pollutants = [
        pollutant
        for pollutant in priority_pollutants
        if pollutants[pollutant]
        / POLLUTANT_THRESHOLDS[pollutant] > 0.75
    ]

    # --------------------------------------------------------
    # RECOMMENDED ACTIONS
    # --------------------------------------------------------

    recommended_actions = []

    if x.pm25 > POLLUTANT_THRESHOLDS["PM2.5"]:

        recommended_actions.append(
            "PM2.5 emission control and filtration"
        )

    if x.pm10 > POLLUTANT_THRESHOLDS["PM10"]:

        recommended_actions.append(
            "dust suppression and particulate control"
        )

    if x.no2 > POLLUTANT_THRESHOLDS["NO2"]:

        recommended_actions.append(
            "combustion efficiency and NO2 control"
        )

    if x.so2 > POLLUTANT_THRESHOLDS["SO2"]:

        recommended_actions.append(
            "low-sulphur fuel and SO2 control"
        )

    if x.co > POLLUTANT_THRESHOLDS["CO"]:

        recommended_actions.append(
            "combustion optimisation and CO monitoring"
        )

    recommended_actions.extend([
        "continuous emission monitoring",
        "energy efficiency",
        "pollution-control equipment"
    ])

    return {

        "status": "success",

        "sector": x.sector,

        "pollutants": pollutant_status,

        "pollution_pressure_score": round(
            pollution_pressure_score,
            2
        ),

        "overall_pollution_risk": (
            pollution_risk
        ),

        "pollutants_above_screening_threshold": (
            exceedance_count
        ),

        "priority_pollutants": (
            priority_pollutants
        ),

        "recommended_actions": (
            recommended_actions
        ),

        "screening_thresholds": (
            POLLUTANT_THRESHOLDS
        ),

        "method": (
            "Pollutant-by-pollutant threshold ratio "
            "and average pollution-pressure screening"
        ),

        "important_note": (
            "This is a development-stage air-pollution "
            "screening tool. The thresholds are not "
            "official regulatory limits and should not "
            "be used for compliance determination. "
            "Actual assessment should use validated "
            "stack or ambient monitoring data and "
            "applicable regulatory standards."
        )
    }
