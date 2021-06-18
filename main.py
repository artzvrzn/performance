from pathlib import Path
from logger import logger
import pandas
from datetime import datetime
import matplotlib.pyplot as plt

BASE_PATH = Path(__file__).resolve().parent
lt22_path = BASE_PATH / 'lt22.xlsx'

logger.debug(lt22_path)

lt22 = pandas.read_excel(lt22_path, usecols=['User1',
                                             'Dest.target quantity',
                                             'Confirmation date',
                                             'Confirmation time',
                                             ]
                         )
lt22['Comb'] = lt22['Confirmation date'].astype('str') + ' ' + lt22['Confirmation time'].astype('str')
print(lt22)
lt22 = lt22[:-1]
lt22['Comb'] = pandas.to_datetime(lt22['Comb'], infer_datetime_format=True)
date_filter = lt22[
    (lt22['Comb'] > pandas.to_datetime('2021-06-10 19:00:00')) &
    (lt22['Comb'] < pandas.to_datetime('2021-06-11 06:40:00'))
]
pivot = date_filter.groupby(['User1', 'Comb'])['Dest.target quantity'].count()
df = pivot.to_frame().reset_index()
df.rename({'Comb': 'Time', 'Dest.target quantity': 'Quantity'}, axis='columns', inplace=True)
df['Time'] = df['Time'].apply(pandas.to_datetime)
df['Time'] = df['Time'].dt.round('H')
new_pivot = df.groupby(['User1', 'Time'])['Quantity'].count()
new_df = new_pivot.to_frame().reset_index()
print(new_df)
new_new_pivot = new_df.pivot_table(index=['Time'], columns=['User1'], values='Quantity')
x = new_new_pivot.reset_index()
print(x)
x.fillna(value=0, inplace=True)
print(x)
for i in range(1, len(x.index)):
    for name in x.columns:
        if name == 'Time':
            pass
        else:
            x.loc[i, name] += x.loc[i-1, name]

print(x)
x.plot(x='Time', y=[a for a in x.columns if a not in ['Time']])
plt.show()
# pivot.assign(Date=pivot['Confirmation time'].dt.round('H'))

# pivot = date_filter.pivot_table(index=['Confirmation time', 'User1'], values='Dest.target quantity', aggfunc='count')

# print(pivot['Dest.target quantity'])
