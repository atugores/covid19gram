import pandas as pd
from sodapy import Socrata
import numpy as np

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("analisi.transparenciacatalunya.cat", "wlktDhyNrB5GfLv8Ry6iQC4xJ")

# Example authenticated client (needed for non-public datasets):
# client = Socrata(analisi.transparenciacatalunya.cat,
#                  MyAppToken,
#                  userame="user@example.com",
#                  password="AFakePassword")

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.

results = client.get("c7sd-zy9j", limit=2000000)

# Convert to pandas DataFrame

# NOM,CODI,DATA,SEXE,GRUP_EDAT,RESIDENCIA,CASOS_CONFIRMAT,PCR,INGRESSOS_TOTAL,INGRESSOS_CRITIC,INGRESSATS_TOTAL,INGRESSATS_CRITIC,EXITUS

cat_df = pd.DataFrame.from_records(results)
cat_df.rename(columns={'data': 'date', 'codi': 'region_code', 'casos_confirmat': 'daily_cases', 'exitus': 'daily_deceased'}, inplace=True)
cat_df['region_code'] = cat_df['region_code'].astype(str)
cat_df['daily_cases'] = pd.to_numeric(cat_df['daily_cases'])
cat_df['daily_deceased'] = pd.to_numeric(cat_df['daily_deceased'])
cat_df['pcr'] = pd.to_numeric(cat_df['pcr'])

max_date = cat_df['date'].max()
pivot_df = cat_df.pivot_table(index=['date', 'region_code'],
                              columns=['sexe', 'grup_edat', 'residencia'], values=['daily_cases', 'daily_deceased', 'pcr'], aggfunc='first')
pivot_df.reset_index(inplace=True)
pivot_df.set_index(['date', 'region_code'], inplace=True)
pivot_df['recovered'] = 0.0
pivot_df.sort_index(inplace=True)
pivot_df = pivot_df.fillna('0')

pivot_df = pivot_df.sum(level=0, axis=1)
# cases acumulated
region_df = pd.read_csv(f"/home/jaume/Feines/covid/cat/catalunya_codes.csv", dtype=str)
region_df.set_index('region_code', inplace=True)
pivot_df = pivot_df.merge(region_df, left_index=True,
                          right_index=True, how='left')
pivot_df.to_csv("/home/jaume/Feines/covid/cat/pivot.csv")

# Filling blanks
new_df = pd.DataFrame()
for region in pivot_df['region'].unique():
    reg_df = pivot_df[pivot_df.region == region]
    reg_df.reset_index(inplace=True)
    # reg_df['date'] = pd.to_datetime(reg_df['date'])
    reg_df.set_index(['date'], inplace=True)
    reg_df.sort_index(inplace=True)
    idx = pd.date_range(reg_df.index.min(), max_date)
    reg_df.index = pd.DatetimeIndex(reg_df.index)
    reg_df = reg_df.reindex(idx, method=None)
    reg_df.reset_index(inplace=True)
    reg_df['region'] = region
    reg_df = reg_df.fillna(0)
    new_df = pd.concat([new_df, reg_df])
new_df['cases'] = new_df.groupby(['region'])['daily_cases'].cumsum()
new_df['deceased'] = new_df.groupby(['region'])['daily_deceased'].cumsum()

new_df.rename(columns={'index': 'date'}, inplace=True)
new_df.set_index(['date', 'region_code'], inplace=True)
new_df.sort_index(inplace=True)
new_df.to_csv("/home/jaume/Feines/covid/cat/test.csv")

df = new_df
pop_df = pd.read_csv(f"/home/jaume/Feines/covid/cat/catalunya_population.csv")
pop_df.set_index('region_name', inplace=True)
df = df.merge(pop_df, left_on='region', right_index=True, how='left')
dates = df.index.get_level_values('date').unique()
for date in dates:
    date_df = df.loc[date]
    total = date_df.sum(min_count=1)
    total['region'] = f'total-catalunya'
    df.loc[(date, 0), df.columns] = total.values
df['cases_per_100k'] = 0.0
df['deceased_per_100k'] = 0.0
df['active_cases_per_100k'] = 0.0
df['cases_per_100k'] = df['cases'] * 100_000 / df['population']
df['deceased_per_100k'] = df['deceased'] * 100_000 / df['population']
df['active_cases'] = df['cases'] - df['recovered'] - df['deceased']
df['active_cases_per_100k'] = df['active_cases'] * 100_000 / df['population']
if 'cases_1' in df.columns:
    for i in range(1, 10):
        df['acum14_cases_' + str(i)] = 0.0
        df['acum14_cases_per_100k_' + str(i)] = 0.0
        df['increase_cases_' + str(i)] = 0.0

if 'hospitalized' in df.columns:
    df['hosp_per_100k'] = df['hospitalized'] * 100_000 / df['population']
    df['increase_hosp'] = 0.0
    df['rolling_hosp'] = 0.0
    df['rolling_hosp_per_100k'] = 0.0

if 'daily_tests' in df.columns:
    df['testing_rate'] = 0.0
    df['positivity_rate'] = 0.0

df['increase_cases'] = 0.0
df['increase_cases_per_100k'] = 0.0
df['rolling_cases'] = 0.0
df['rolling_cases_per_100k'] = 0.0
df['Rt'] = 0.0
df['epg'] = 0.0
df['acum14_cases'] = 0.0
df['acum14_cases_per_100k'] = 0.0
df['acum14_hosp'] = 0.0
df['acum14_hosp_per_100k'] = 0.0

df['increase_deceased'] = 0.0
df['rolling_deceased'] = 0.0
df['rolling_deceased_per_100k'] = 0.0
df['acum14_deceased'] = 0.0
df['acum14_deceased_per_100k'] = 0.0

for region in df['region'].unique():
    reg_df = df[df.region == region]
    # cases
    increase = reg_df['cases'] - reg_df['cases'].shift(1)
    increase[increase < 0] = 0.0
    rolling = increase.rolling(window=7).mean()
    df['increase_cases'].mask(df.region == region, increase, inplace=True)
    df['rolling_cases'].mask(df.region == region, rolling, inplace=True)
    df['increase_cases_per_100k'] = df['increase_cases'] * 100_000 / df['population']
    df['rolling_cases_per_100k'] = df['rolling_cases'] * 100_000 / df['population']
    # cases acum
    rolling = increase.rolling(window=14).sum()
    df['acum14_cases'].mask(df.region == region, rolling, inplace=True)
    df['acum14_cases_per_100k'] = df['acum14_cases'] * 100_000 / df['population']
    # EPG
    p = increase.rolling(3).sum() / (increase.rolling(7).sum() - increase.rolling(4).sum())
    p.loc[~np.isfinite(p)] = np.nan
    p.fillna(method='ffill')
    p7 = p.rolling(7).mean()
    epg = p7 * df['acum14_cases']
    df['Rt'].mask(df.region == region, p7, inplace=True)
    df['epg'].mask(df.region == region, epg, inplace=True)
    # cases history
    if 'cases_1' in df.columns:
        for i in range(1, 10):
            increase = reg_df['cases_' + str(i)] - reg_df['cases_' + str(i)].shift(1)
            increase[increase < 0] = 0.0
            df['increase_cases_' + str(i)].mask(df.region == region, increase, inplace=True)
            rolling = increase.rolling(window=14).sum()
            df['acum14_cases_' + str(i)].mask(df.region == region, rolling, inplace=True)
            df['acum14_cases_per_100k_' + str(i)] = df['acum14_cases_' + str(i)] * 100_000 / df['population']
    # deceased
    increase = reg_df['deceased'] - reg_df['deceased'].shift(1)
    increase[increase < 0] = 0.0
    rolling = increase.rolling(window=7).mean()
    df['increase_deceased'].mask(df.region == region, increase, inplace=True)
    df['rolling_deceased'].mask(df.region == region, rolling, inplace=True)
    df['rolling_deceased_per_100k'] = df['rolling_deceased'] * 100_000 / df['population']
    # deceased acum
    rolling = increase.rolling(window=14).sum()
    df['acum14_deceased'].mask(df.region == region, rolling, inplace=True)
    df['acum14_deceased_per_100k'] = df['acum14_deceased'] * 100_000 / df['population']
    # test positivity rates
    if 'daily_tests' in df.columns:
        rolling = reg_df['daily_tests'].rolling(window=7).sum()
        df['testing_rate'].mask(df.region == region, increase, inplace=True)
        df['testing_rate'] = df['testing_rate'] * 100_000 / df['population']
        rolling_positive = reg_df['increase_cases'].rolling(window=7).sum()
        pos_rate = rolling_positive / rolling
        df['positivity_rate'].mask(df.region == region, pos_rate, inplace=True)
    # hospitalized
    if 'hospitalized' in df.columns:
        increase = reg_df['hospitalized'] - reg_df['hospitalized'].shift(1)
        increase[increase < 0] = 0.0
        rolling = increase.rolling(window=7).mean()
        df['increase_hosp'].mask(df.region == region, increase, inplace=True)
        df['rolling_hosp'].mask(df.region == region, rolling, inplace=True)
        df['rolling_hosp_per_100k'] = df['rolling_hosp'] * 100_000 / df['population']
        # hosp acum
        rolling = increase.rolling(window=14).sum()
        df['acum14_hosp'].mask(df.region == region, rolling, inplace=True)
        df['acum14_hosp_per_100k'] = df['acum14_hosp'] * 100_000 / df['population']

df.sort_index(inplace=True)
df.to_csv(f"/home/jaume/Feines/covid/cat/catalunya_covid19gram.csv")
