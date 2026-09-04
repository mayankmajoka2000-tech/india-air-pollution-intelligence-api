@router.post("/anomaly")
def anomaly(values: list[float]):
    if not values:
        return {
            "anomaly_count": 0,
            "indices": [],
            "method": "IQR"
        }

    import numpy as np

    a = np.array(values, dtype=float)

    # Calculate first and third quartiles
    q1 = np.percentile(a, 25)
    q3 = np.percentile(a, 75)

    # Interquartile range
    iqr = q3 - q1

    # Define anomaly boundaries
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Identify anomalous observations
    idx = np.where(
        (a < lower_bound) | (a > upper_bound)
    )[0].tolist()

    return {
        "anomaly_count": len(idx),
        "indices": idx,
        "method": "IQR",
        "lower_bound": round(float(lower_bound), 2),
        "upper_bound": round(float(upper_bound), 2)
    }
