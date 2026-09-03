import pandas as pd
def quality_report(df):
    return {
        "rows": len(df),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_summary": df.select_dtypes("number").describe().to_dict()
    }
