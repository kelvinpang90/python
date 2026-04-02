import pandas as pd

df = pd.read_csv('./csv_data/imdb_top250_2026-03-26.csv')
# print(df.head(n=100))
# print(df.info())
# print(df.describe())
# print(df.shape)
# print(df.columns)
print(df[df["Rating"]>=9])
print(df[df["Rating"].between(8,9)])

# df.set_index('Ranking')
# df.index.name = 'Ranking_index'
# df.reset_index()
# df.index.name = "index"
# df.to_csv('./csv_data/imdb_top250_2026-03-26.csv')