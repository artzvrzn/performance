import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as dts
import matplotlib.ticker as ticker
from datetime import date, timedelta

from logger import logger
from users import users
from chrome_driver import LT22Run

DATE_BEFORE = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
DATE_TODAY = date.today().strftime('%Y-%m-%d')


class LT22Reader:

    def __init__(self, path_to_lt22):
        self.lt22_df = pandas.read_excel(path_to_lt22)[:-2]
        self.lt22_df.dropna(subset=['Source storage unit'], inplace=True)
        print(self.lt22_df['Source storage unit'])
        self.lt22_df.loc[:, 'Time'] = (self.lt22_df.loc[:, 'Confirmation date'].astype('str') +
                                       ' ' +
                                       self.lt22_df.loc[:, 'Confirmation time'].astype('str'))
        self.lt22_df.loc[:, 'Time'] = pandas.to_datetime(self.lt22_df.loc[:, 'Time']).dt.floor('15min')
        self.lt22_df.rename({'Source storage unit': 'Quantity'}, axis='columns', inplace=True)
        self.pivot_df = self._to_pivot()

    def _to_pivot(self):
        lt22_night_df = self.lt22_df[
            (self.lt22_df['Time'] > pandas.to_datetime(f'{DATE_BEFORE} 18:50:00')) &
            (self.lt22_df['Time'] < pandas.to_datetime(f'{DATE_TODAY} 07:00:00'))
            ]
        pallet_by_time = lt22_night_df.groupby(['User.1', 'Time'])['Quantity'].count()
        pallet_by_time_df = pallet_by_time.to_frame().reset_index()

        lt22_pivot = pallet_by_time_df.pivot_table(index=['Time'], columns=['User.1'], values='Quantity')
        pivot_df = lt22_pivot.reset_index()
        pivot_df.fillna(value=0, inplace=True)

        # renaming users to their lastnames
        pivot_df.rename({code: name for code, name in users.items()}, axis='columns', inplace=True)
        # increasing each user's quantity by quantity before
        for i in range(1, len(pivot_df.index)):
            for name in pivot_df.columns:
                if name == 'Time':
                    pass
                else:
                    pivot_df.loc[i, name] += pivot_df.loc[i - 1, name]
        logger.debug(pivot_df)
        return pivot_df

    def get_plot(self):
        # setting up style for plot
        plt.style.use('ggplot')
        plt.style.use('seaborn-notebook')
        date_formatter = dts.DateFormatter('%H:%M')
        date_locator = dts.HourLocator(interval=1)

        # making plot showing amount of pallets by time for each user
        lt22_plot = self.pivot_df.plot(
            x='Time',
            y=[a for a in self.pivot_df.columns if a not in ['Time']],
            xlabel='Время',
            ylabel='Поддоны',
            colormap='Set1',
        )

        lt22_plot.xaxis.set_major_locator(date_locator)
        lt22_plot.xaxis.set_major_formatter(date_formatter)
        lt22_plot.yaxis.tick_right()
        lt22_plot.yaxis.set_major_locator(ticker.MultipleLocator(base=25.0))

        plt.show()


if __name__ == '__main__':
    lt22_extraction = LT22Run()
    lt22_extraction.execute()
    file_path = lt22_extraction.file_name
    reader = LT22Reader(file_path)
    reader.get_plot()
