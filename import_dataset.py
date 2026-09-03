from pathlib import Path
import pandas as pd
p=Path("data/india_air_quality_total_320000.csv")
df=pd.read_csv(p)
print("Loaded records:",len(df))
print(df.head())
print("Missing cells:",int(df.isna().sum().sum()))
