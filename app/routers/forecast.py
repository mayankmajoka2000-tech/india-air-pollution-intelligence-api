# ============================================================
# LOAD TRAINED MODEL
# ============================================================

def load_model():

    if not MODEL_PATH.exists():

        raise HTTPException(
            status_code=503,
            detail=(
                "Trained Random Forest model is not available. "
                "Please deploy the trained model artifact first."
            )
        )

    try:

        return joblib.load(MODEL_PATH)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load trained ML model: {str(e)}"
        )
