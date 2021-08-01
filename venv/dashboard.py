import pandas as pd

df = pd.read_json('Yahoo_Financials.json', orient='split')
print(df)