from pathlib import Path
from logger import logger
import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as dts
from users import users

BASE_PATH = Path(__file__).resolve().parent
lt22_path = BASE_PATH / 'lt24.xlsx'
logger.debug(lt22_path)

# setting up style for plot
plt.style.use('ggplot')
plt.style.use('seaborn-notebook')
date_formatter = dts.DateFormatter('%H:%M')
date_locator = dts.HourLocator(interval=1)

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

lt22_pivot = pallet_by_round_time_df.pivot_table(index=['Time'], columns=['User.1'], values='Quantity')
lt22_pivot_df = lt22_pivot.reset_index()
lt22_pivot_df.fillna(value=0, inplace=True)
# renaming users to their lastnames
lt22_pivot_df.rename({code: name for code, name in users.items()}, axis='columns', inplace=True)

# increasing each user's quantity by quantity before
for i in range(1, len(lt22_pivot_df.index)):
    for name in lt22_pivot_df.columns:
        if name == 'Time':
            pass
        else:
            lt22_pivot_df.loc[i, name] += lt22_pivot_df.loc[i - 1, name]
logger.debug(lt22_pivot_df)

# making plot showing amount of pallets by time for each user
lt22_plot = lt22_pivot_df.plot(
    x='Time',
    y=[a for a in lt22_pivot_df.columns if a not in ['Time']],
    xlabel='Время',
    ylabel='Поддоны',
    colormap='Set1',
)

lt22_plot.xaxis.set_major_locator(date_locator)
lt22_plot.xaxis.set_major_formatter(date_formatter)
lt22_plot.yaxis.tick_right()

plt.show()