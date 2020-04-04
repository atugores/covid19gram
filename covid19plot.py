#!/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import date
import os

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
sns.set_context("paper")
sns.set_style("whitegrid")


class COVID19Plot(object):

    _images_dir = None
    _csv_path = None
    _csv_ts = None
    _df = None

    def __init__(self, data_directory='datasets/COVID 19', images_dir='images/'):
        # load csv
        # df = pd.read_csv('datasets/COVID 19/ccaa_covid19_casos_long.csv')
        self._csv_path = data_directory + '/ccaa_covid19_casos_long.csv'
        self._reload_data()
        self._images_dir = images_dir

    def _reload_data(self):
        self._df = pd.read_csv(self._csv_path)
        # convert date to datetime and set index
        self._df['fecha']= pd.to_datetime(self._df['fecha']) 
        self._df.set_index('fecha', inplace=True)

        self._csv_ts = int(os.path.getmtime(self._csv_path))

    def get_regions(self):
        return list(self._df.CCAA.unique())

    def _generate_image(self, df_reduced, region, image_path):
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        plt.bar(df_reduced.index, df_reduced['increase'], alpha=0.3, label='Daily increment')
        plt.fill_between(df_reduced.index, 0, df_reduced['rolling'], color='red', alpha=0.5, label='Rolling avg increment (3 days)')
        plt.plot(df_reduced['rolling'], color='red')
        ax.set_xlim(np.datetime64('2020-03-01'))
        ax.set_ylabel('Cases')
        ax.figure.autofmt_xdate()
        ax.legend(loc='upper left')
        plt.title(f'Increment de contagis a {region}', fontsize=20)
        plt.savefig(image_path)
        plt.close()
        return 

    def generate_daily_cases_img(self, region):
        # check if data source has been modified, and reload it if necessary
        if int(os.path.getmtime(self._csv_path)) != self._csv_ts:
            self._reload_data()

        # check if image has already been generated
        image_fpath = self._images_dir + '/' + region + '_cases_' + str(self._csv_ts) + '.png'
        if os.path.isfile(image_fpath):
            return image_fpath

        # regenerate image

        # select region
        df_reduced = self._df[self._df.CCAA==region]
        # calculate daily increase and rolling avg
        df_reduced['increase'] = df_reduced['total'] - df_reduced['total'].shift(1)
        df_reduced['rolling'] = df_reduced.rolling(window=3).mean()['increase']

        self._generate_image(df_reduced, region, image_fpath)
        return image_fpath
