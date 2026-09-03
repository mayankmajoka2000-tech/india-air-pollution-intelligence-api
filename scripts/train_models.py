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
    "PM10",
    "NO2",
    "SO2",
    "CO",
    "O3",
    "NH3",
    "Pb",
    "temperature",
    "humidity",
    "wind_speed",
    "wind_direction",
    "rainfall",
    "pressure"
]

target = "PM2.5"

# Keep only columns available in dataset
features = [col for col in features if col in df.columns]

print("\nFeatures used:")
print(features)

print("\nTarget variable:")
print(target)


# ============================================================
# 4. PREPARE X AND y
# ============================================================

X = df[features]
y = df[target]

print("\nX shape:", X.shape)
print("y shape:", y.shape)


# ============================================================
# 5. TRAIN-TEST SPLIT
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
# 6. TRAIN RANDOM FOREST MODEL
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
# 7. PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

y_pred = model.predict(X_test)


# ============================================================
# 8. MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")


# ============================================================
# 9. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print("\nFeature Importance:")
print(importance.to_string(index=False))


# ============================================================
# 10. SAVE MODEL RESULTS
# ============================================================

OUTPUT_PATH = Path("data/model_results.csv")

importance.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nFeature importance saved to:")
print(OUTPUT_PATH)

print("\nTraining pipeline completed successfully.")
