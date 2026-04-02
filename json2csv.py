import pandas as pd

df = pd.read_json("json_data/scholar_results.json")
df.to_csv("./csv_data/scholar_results.csv", index=False, encoding="utf-8-sig")