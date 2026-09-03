def model_catalog():
    return {
        "tabular":["XGBoost","LightGBM","Random Forest","CatBoost"],
        "time_series":["LSTM","GRU","Transformer"],
        "explainability":["SHAP"],
        "tracking":["MLflow"]
    }
