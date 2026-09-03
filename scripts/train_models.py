from pathlib import Path
import time
import joblib

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor


# ============================================================
# 1. PATHS
# ============================================================

DATA_PATH = Path("data/india_air_quality_total_320000.csv")
MODEL_DIR = Path("data/models")

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("=" * 70)
print("INDIA AIR POLLUTION ML MODEL COMPARISON")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully.")
print("Records:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 3. DATA QUALITY
# ============================================================

print("\nChecking data quality...")

print("Missing values:", int(df.isna().sum().sum()))

df = df.dropna()

print("Records after removing missing values:", len(df))


# ============================================================
# 4. FEATURES AND TARGET
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
# 5. VERIFY COLUMNS
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
# 6. PREPARE DATA
# ============================================================

X = df[features]
y = df[target]

print("\nX shape:", X.shape)
print("y shape:", y.shape)


# ============================================================
# 7. TRAIN-TEST SPLIT
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
# 8. DEFINE MODELS
# ============================================================

models = {

    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    ),

    "XGBoost": XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        objective="reg:squarederror"
    ),

    "LightGBM": LGBMRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbosity=-1
    )
}


# ============================================================
# 9. TRAIN MODELS
# ============================================================

results = []
feature_importance_results = {}

trained_models = {}

for name, model in models.items():

    print("\n" + "=" * 70)
    print(f"TRAINING: {name}")
    print("=" * 70)

    start_time = time.time()

    model.fit(
        X_train,
        y_train
    )

    training_time = time.time() - start_time

    print("Training completed.")

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    y_pred = model.predict(X_test)

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

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

    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")
    print(f"Training Time: {training_time:.2f} seconds")

    results.append({
        "model": name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "training_time_seconds": training_time
    })

    trained_models[name] = model

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    if hasattr(model, "feature_importances_"):

        importance = pd.DataFrame({
            "feature": features,
            "importance": model.feature_importances_
        })

        importance = importance.sort_values(
            "importance",
            ascending=False
        )

        feature_importance_results[name] = importance


# ============================================================
# 10. MODEL COMPARISON
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "R2",
    ascending=False
)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(index=False)
)


# ============================================================
# 11. SELECT BEST MODEL
# ============================================================

best_model_name = results_df.iloc[0]["model"]
best_model = trained_models[best_model_name]

print("\n" + "=" * 70)
print("BEST MODEL")
print("=" * 70)

print("Model:", best_model_name)
print(
    f"MAE: {results_df.iloc[0]['MAE']:.4f}"
)
print(
    f"RMSE: {results_df.iloc[0]['RMSE']:.4f}"
)
print(
    f"R²: {results_df.iloc[0]['R2']:.4f}"
)


# ============================================================
# 12. SAVE BEST MODEL
# ============================================================

BEST_MODEL_PATH = MODEL_DIR / "best_pm25_model.joblib"

joblib.dump(
    best_model,
    BEST_MODEL_PATH
)

print("\nBest model saved to:")
print(BEST_MODEL_PATH)


# ============================================================
# 13. SAVE FEATURE LIST
# ============================================================

FEATURE_PATH = MODEL_DIR / "model_features.csv"

pd.DataFrame({
    "feature": features
}).to_csv(
    FEATURE_PATH,
    index=False
)

print("Model feature list saved to:")
print(FEATURE_PATH)


# ============================================================
# 14. SAVE MODEL COMPARISON
# ============================================================

RESULTS_PATH = Path(
    "data/model_comparison.csv"
)

results_df.to_csv(
    RESULTS_PATH,
    index=False
)

print("Model comparison saved to:")
print(RESULTS_PATH)


# ============================================================
# 15. SAVE FEATURE IMPORTANCE
# ============================================================

for model_name, importance_df in feature_importance_results.items():

    safe_name = (
        model_name
        .lower()
        .replace(" ", "_")
    )

    output_path = Path(
        f"data/{safe_name}_feature_importance.csv"
    )

    importance_df.to_csv(
        output_path,
        index=False
    )

    print(
        f"{model_name} feature importance saved to:"
    )

    print(output_path)


# ============================================================
# 16. FINAL STATUS
# ============================================================

print("\n" + "=" * 70)
print("MODEL TRAINING AND SAVING COMPLETED SUCCESSFULLY")
print("=" * 70)

print("Selected model:", best_model_name)
print("Saved model:", BEST_MODEL_PATH)
