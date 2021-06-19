from pathlib import Path
from logger import logger
import pandas
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as dts
from matplotlib import cm

BASE_PATH = Path(__file__).resolve().parent
lt22_path = BASE_PATH / 'lt24.xlsx'

logger.debug(lt22_path)
plt.style.use('ggplot')
lt22_df = pandas.read_excel(lt22_path)[:-1]
lt22_df.loc[:, 'Time'] = lt22_df['Confirmation date'].astype('str') + ' ' + lt22_df['Confirmation time'].astype('str')
lt22_df.loc[:, 'Time'] = pandas.to_datetime(lt22_df['Time'])
lt22_df.rename({'Dest.target quantity': 'Quantity'}, axis='columns', inplace=True)

lt22_night_df = lt22_df[
    (lt22_df['Time'] > pandas.to_datetime('2021-06-18 19:00:00')) &
    (lt22_df['Time'] < pandas.to_datetime('2021-06-19 06:55:00'))
    ]

pallet_by_time = lt22_night_df.groupby(['User.1', 'Time'])['Quantity'].count()
pallet_by_time_df = pallet_by_time.to_frame().reset_index()

pallet_by_time_df.loc[:, 'Time'] = pallet_by_time_df['Time'].dt.floor('30min')

pallet_by_round_time = pallet_by_time_df.groupby(['User.1', 'Time'])['Quantity'].count()
pallet_by_round_time_df = pallet_by_round_time.to_frame().reset_index()

new_new_pivot = pallet_by_round_time_df.pivot_table(index=['Time'], columns=['User.1'], values='Quantity')
x = new_new_pivot.reset_index()

x.fillna(value=0, inplace=True)

for i in range(1, len(x.index)):
    for name in x.columns:
        if name == 'Time':
            pass
        else:
            x.loc[i, name] += x.loc[i-1, name]

ax = x.plot(x='Time', y=[a for a in x.columns if a not in ['Time']], xlabel='Время', ylabel='Поддоны', colormap='Set1')

date_formatter = dts.DateFormatter('%H:%M')
date_locator = dts.HourLocator(interval=1)
ax.xaxis.set_major_locator(date_locator)
ax.xaxis.set_major_formatter(date_formatter)
ax.yaxis.tick_right()
print(x)


plt.show()
plt.style.use('seaborn-notebook')
# pivot.assign(Date=pivot['Confirmation time'].dt.round('H'))

# pivot = date_filter.pivot_table(index=['Confirmation time', 'User1'], values='Dest.target quantity', aggfunc='count')

# print(pivot['Dest.target quantity'])
