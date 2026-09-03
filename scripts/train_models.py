from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. LOAD DATASET
# ============================================================

DATA_PATH = Path("data/india_air_quality_total_320000.csv")

print("=" * 60)
print("INDIA AIR POLLUTION ML TRAINING PIPELINE")
print("=" * 60)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully.")
print("Records:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 2. DATA QUALITY CHECK
# ============================================================

print("\nChecking data quality...")

print("Missing values:", int(df.isna().sum().sum()))

df = df.dropna()

print("Records after removing missing values:", len(df))


# ============================================================
# 3. FEATURE SELECTION
# ============================================================

features = [
    "PM10_ug_m3",
    "NO2_ug_m3",
    "SO2_ug_m3",
    "CO_mg_m3",
    "O3_ug_m3",
    "NH3_ug_m3",
    "Pb_ug_m3",
    "temperature_C",
    "relative_humidity_pct",
    "wind_speed_m_s",
    "wind_direction_deg",
    "rainfall_mm",
    "pressure_hPa"
]

target = "PM25_ug_m3"


# ============================================================
# 4. VERIFY REQUIRED COLUMNS
# ============================================================

required_columns = features + [target]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


print("\nFeatures used:")

for feature in features:
    print("-", feature)

print("\nTarget variable:")
print("-", target)


# ============================================================
# 5. PREPARE X AND y
# ============================================================

X = df[features]
y = df[target]

print("\nX shape:", X.shape)
print("y shape:", y.shape)


# ============================================================
# 6. TRAIN-TEST SPLIT
# ============================================================

print("\nCreating train-test split...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))


# ============================================================
# 7. TRAIN RANDOM FOREST MODEL
# ============================================================

print("\nTraining Random Forest model...")

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Model training completed.")


# ============================================================
# 8. GENERATE PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

y_pred = model.predict(X_test)


# ============================================================
# 9. MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)

r2 = r2_score(
    y_test,
    y_pred
)


print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")


# ============================================================
# 10. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)


print("\n" + "=" * 60)
print("FEATURE IMPORTANCE")
print("=" * 60)

print(
    importance.to_string(index=False)
)


# ============================================================
# 11. SAVE MODEL RESULTS
# ============================================================

OUTPUT_PATH = Path(
    "data/model_results.csv"
)

importance.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nFeature importance saved to:")
print(OUTPUT_PATH)


# ============================================================
# 12. FINAL STATUS
# ============================================================

print("\n" + "=" * 60)
print("TRAINING PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 60)
