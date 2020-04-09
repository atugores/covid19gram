#!/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import date
import os
from gettext import gettext as _
import gettext

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
import seaborn as sns
sns.set_context("paper")
sns.set_style("whitegrid")
matplotlib.use('Agg')


class COVID19Plot(object):

    LANGUAGES = ['ca', 'es', 'en']
    PLOT_TYPES = [
        'daily_cases',
        'daily_deceased',
        'active_recovered_deceased',
        'active',
        'deceased',
        'recovered',
        'cases_normalized'
    ]

    MULTIREGION_PLOT_TYPES = [
        'cases_normalized',
        'deceased_normalized',
    ]

    _images_dir = None
    _source_path = None
    _source_ts = None
    _footer_font = None
    _translations = {}
    _df = None
    _global_df = None

    def __init__(self, data_directory='data', images_dir='images/'):
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        self._source_path = data_directory
        self._load_translations()
        self._reload_data()
        self._reload_global_data()
        self._images_dir = images_dir
        self._footer_font = FontProperties()
        self._footer_font.set_family('serif')
        self._footer_font.set_style('italic')

    def _reload_data(self):
        csv_path = self._source_path + '/ccaa_covid19_casos_long.csv'
        if not os.path.isfile(csv_path):
            raise RuntimeError('Datasource not found')

        self._df = pd.read_csv(csv_path)
        # convert date to datetime and set index
        self._df['fecha']= pd.to_datetime(self._df['fecha'])
        self._df.set_index(['fecha', 'cod_ine'], inplace=True)
        self._df.rename(columns={'total': 'cases'}, inplace=True)
        # column recovered
        altas_df = pd.read_csv(self._source_path + '/ccaa_covid19_altas_long.csv')
        altas_df['fecha']= pd.to_datetime(altas_df['fecha'])
        altas_df.set_index(['fecha', 'cod_ine'], inplace=True)
        altas_df.columns = ['CCAA_altas', 'recovered']
        self._df = self._df.merge(altas_df, left_index=True, right_index=True, how='left')
        self._df.drop(columns=['CCAA_altas'], inplace=True)
        # column deceased
        fac_df = pd.read_csv(self._source_path + '/ccaa_covid19_fallecidos_long.csv')
        fac_df['fecha']= pd.to_datetime(fac_df['fecha'])
        fac_df.set_index(['fecha', 'cod_ine'], inplace=True)
        fac_df.columns = ['CCAA_fac', 'deceased']
        self._df = self._df.merge(fac_df, left_index=True, right_index=True, how='left')
        self._df.drop(columns=['CCAA_fac'], inplace=True)
        # column population
        pob_df = pd.read_csv(self._source_path + '/ccaa_poblacion.csv')
        pob_df.set_index('cod_ine', inplace=True)
        self._df = self._df.merge(pob_df, left_index=True, right_index=True, how='left')
        self._df['cases_per_100k'] = self._df['cases'] * 100_000 / self._df['population']

        self._df.fillna(0, inplace=True)
        self._df.sort_index()
        self._df['active_cases'] = self._df['cases'] - self._df['recovered'] - self._df['deceased']

        self._source_ts = int(os.path.getmtime(csv_path))

    def _reload_global_data(self):
        csv_path = self._source_path + '/global_covid19_casos_long.csv'
        if not os.path.isfile(csv_path):
            raise RuntimeError('Datasource not found')

        self._global_df = pd.read_csv(csv_path)
        # convert date to datetime and set index
        self._global_df['fecha']= pd.to_datetime(self._global_df['fecha'])
        self._global_df.set_index(['fecha', 'cod_ine'], inplace=True)
        self._global_df.rename(columns={'total': 'cases'}, inplace=True)
        # column recovered
        altas_df = pd.read_csv(self._source_path + '/global_covid19_altas_long.csv')
        altas_df['fecha']= pd.to_datetime(altas_df['fecha'])
        altas_df.set_index(['fecha', 'cod_ine'], inplace=True)
        altas_df.columns = ['CCAA_altas', 'recovered']
        self._global_df = self._global_df.merge(altas_df, left_index=True, right_index=True, how='left')
        self._global_df.drop(columns=['CCAA_altas'], inplace=True)
        # column deceased
        fac_df = pd.read_csv(self._source_path + '/global_covid19_fallecidos_long.csv')
        fac_df['fecha']= pd.to_datetime(fac_df['fecha'])
        fac_df.set_index(['fecha', 'cod_ine'], inplace=True)
        fac_df.columns = ['CCAA_fac', 'deceased']
        self._global_df = self._global_df.merge(fac_df, left_index=True, right_index=True, how='left')
        self._global_df.drop(columns=['CCAA_fac'], inplace=True)

        self._global_df.fillna(0, inplace=True)
        self._global_df.sort_index()
        self._global_df['active_cases'] = self._global_df['cases'] - self._global_df['recovered'] - self._global_df['deceased']

        self._source_ts = int(os.path.getmtime(csv_path))

    def _check_new_data(self):
        csv_path = self._source_path + '/ccaa_covid19_casos_long.csv'
        if not os.path.isfile(csv_path):
            raise RuntimeError('Datasource not found')
        if int(os.path.getmtime(csv_path)) != self._source_ts:
            self._reload_data()

    def _load_translations(self):
        for language in self.LANGUAGES:
            translation = gettext.translation('messages', localedir='locales', languages=[language])
            translation.install()
            self._translations[language] = translation

    def get_regions(self):
        return list(self._df.CCAA.unique())

    def get_global_regions(self):
        return list(self._global_df.CCAA.unique())

    def generate_plot(self, plot_type, region,language='en'):
        if plot_type not in self.PLOT_TYPES:
            raise RuntimeError('Plot type is not recognized')

        # check if data source has been modified, and reload it if necessary
        self._check_new_data()

        # check if image has already been generated
        image_fpath = f"{self._images_dir}/{language}_{region}_{plot_type}_{self._source_ts}.png"
        if os.path.isfile(image_fpath):
            return image_fpath

        # select region
        if region in self.get_regions():
            df_reduced = self._get_plot_data(plot_type, region)
        elif region in self.get_global_regions():
            df_reduced = self._get_global_plot_data(plot_type, region)
        self._plot(plot_type, region, language, df_reduced, image_fpath)
        return image_fpath

    def generate_multiregion_plot(self, plot_type, regions, language='en'):
        if plot_type not in self.MULTIREGION_PLOT_TYPES:
            raise RuntimeError('Plot type is not recognized')

        # check if data source has been modified, and reload it if necessary
        self._check_new_data()

        # check if image has already been generated
        region = '-'.join([region for region in sorted(regions)])
        image_fpath = f"{self._images_dir}/{language}_{region}_{plot_type}_{self._source_ts}.png"
        if os.path.isfile(image_fpath):
            return image_fpath

        self._multiregion_plot(plot_type, regions, language, image_fpath)
        return image_fpath

    def _get_plot_data(self, plot_type, region):
        df_reduced = self._df[self._df.CCAA==region]
        if plot_type == 'daily_cases':
            # calculate daily increase and rolling avg
            df_reduced['increase'] = df_reduced['cases'] - df_reduced['cases'].shift(1)
            df_reduced['rolling'] = df_reduced.rolling(window=3).mean()['increase']
        elif plot_type == 'daily_deceased':
            # calculate daily increase and rolling avg
            df_reduced['increase'] = df_reduced['deceased'] - df_reduced['deceased'].shift(1)
            df_reduced['rolling'] = df_reduced.rolling(window=3).mean()['increase']
        return df_reduced

    def _get_global_plot_data(self, plot_type, region):
        df_reduced = self._global_df[self._global_df.CCAA==region]
        if plot_type == 'daily_cases':
            # calculate daily increase and rolling avg
            df_reduced['increase'] = df_reduced['cases'] - df_reduced['cases'].shift(1)
            df_reduced['rolling'] = df_reduced.rolling(window=3).mean()['increase']
        elif plot_type == 'daily_deceased':
            # calculate daily increase and rolling avg
            df_reduced['increase'] = df_reduced['deceased'] - df_reduced['deceased'].shift(1)
            df_reduced['rolling'] = df_reduced.rolling(window=3).mean()['increase']
        return df_reduced

    def _plot(self, plot_type, region, language, df, image_path):
        # set translation to current language
        _ = self._translations[language].gettext

        fig, ax = plt.subplots(figsize=(12, 6))
        x = df.index.get_level_values('fecha')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        title = None
        y_label = None

        if plot_type == 'daily_cases':
            title = _('Cases increase at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['increase'], alpha=0.3, width=0.9, label=_('Daily increment'))
            plt.fill_between(x, 0, df['rolling'], color='red', alpha=0.5, label=_('Increment rolling avg (3 days)'))
            plt.plot(x, df['rolling'], color='red')
            ax.annotate(f"{df['increase'][-1]:0,.0f}", xy=(x[-1]- np.timedelta64(12,'h'), df['increase'][-1]))
        elif plot_type == 'daily_deceased':
            title = _('Daily deaths evolution at {region}').format(region=_(region))
            y_label = _('Deaths')
            plt.bar(x, df['increase'], alpha=0.5, width=0.9, color='red', label=_('Daily deaths'))
            plt.fill_between(x, 0, df['rolling'], color='red', alpha=0.2, label=_('Deaths rolling avg (3 days)'))
            plt.plot(x, df['rolling'], color='red')
            ax.annotate(f"{df['increase'][-1]:0,.0f}", xy=(x[-1]- np.timedelta64(12,'h'), df['increase'][-1]))
        elif plot_type == 'active_recovered_deceased':
            title = _('Active cases, recovered and deceased at {region}').format(region=_(region))
            y_label = _('Cases')
            alpha = 0.3
            plt.fill_between(x, 0, df['active_cases'], alpha=alpha, label=_('Currently infected'))
            plt.plot(x, df['active_cases'])
            ax.annotate(f"{df['active_cases'][-1]:0,.0f}", xy=(x[-1], df['active_cases'][-1]))
            plt.fill_between(x, 0, df['recovered'], color='g', alpha=alpha, label=_('Recovered'))
            plt.plot(x, df['recovered'], color='g')
            ax.annotate(f"{df['recovered'][-1]:0,.0f}", xy=(x[-1], df['recovered'][-1]))
            plt.fill_between(x, 0, df['deceased'], color='red', alpha=alpha, label=_('Deceased'))
            plt.plot(x, df['deceased'], color='red')
            ax.annotate(f"{df['deceased'][-1]:0,.0f}", xy=(x[-1], df['deceased'][-1]))
            # ax.set_ylim(top=np.max(df['active_cases'])*1.05)
            # ax.bar(x, df['active_cases'], width=width, alpha=alpha, label=_('Currently infected'))
            # ax.bar(x, df['recovered'], color='g', width=width, alpha=alpha, label=_('Recovered'))
            # ax.bar(x + np.timedelta64(11,'h'), df['deceased'], color='r', width=width, alpha=alpha, label=_('Deceased'))
        elif plot_type == 'active':
            title = _('Active cases at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['active_cases'], alpha=0.5, width=1, label=_('Active cases'))
            ax.annotate(f"{df['active_cases'][-1]:0,.0f}", xy=(x[-1]  - np.timedelta64(12,'h'), df['active_cases'][-1]))
        elif plot_type == 'recovered':
            title = _('Recovered cases at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['recovered'], alpha=0.5, width=1, color='g', label=_('Recovered cases'))
            ax.annotate(f"{df['recovered'][-1]:0,.0f}", xy=(x[-1] - np.timedelta64(12,'h'), df['recovered'][-1]))
        elif plot_type == 'deceased':
            title = _('Deaths evolution at {region}').format(region=_(region))
            y_label = _('Deaths')
            plt.bar(x, df['deceased'], alpha=0.5, width=1, color='r', label=_('Deceased'))
            ax.annotate(f"{df['deceased'][-1]:0,.0f}", xy=(x[-1]- np.timedelta64(12,'h'), df['deceased'][-1]))
        elif plot_type == 'cases_normalized':
            title = _('Cases per 100k inhabitants at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['cases_per_100k'], alpha=0.5, width=1, label=_('Active cases'))
            ax.annotate(f"{df['cases_per_100k'][-1]:0,.0f}", xy=(x[-1]  - np.timedelta64(12,'h'), df['cases_per_100k'][-1]))

        plt.title(title, fontsize=26)
        ax.set_ylabel(y_label,fontsize=15)
        ax.set_xlim(np.datetime64('2020-03-01'))
        ax.figure.autofmt_xdate()
        ax.legend(loc='upper left',fontsize=17)
        if region in self.get_regions():
            self._add_footer(ax)
        elif region in self.get_global_regions():
            self._add_global_footer(ax)
        plt.savefig(image_path)
        plt.close()

    def _multiregion_plot(self, plot_type, regions, language, image_path):
        # set translation to current language
        _ = self._translations[language].gettext

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        title = None
        y_label = None
        legend = True

        if plot_type == 'cases_normalized':
            legend = False
            title = _('Cases per 100k inhabitants')
            y_label = _('Cases')
            for region in regions:                
                df_region = self._df[self._df.CCAA==region]
                x = df_region.index.get_level_values('fecha')
                plt.plot(x, df_region['cases_per_100k'])
                region_name = _(region)
                ax.annotate(f"{df_region['cases_per_100k'][-1]:0,.0f} ({region_name})", xy=(x[-1]  - np.timedelta64(12,'h'), df_region['cases_per_100k'][-1]))
        elif plot_type == 'deceased_normalized':
            legend = False
            title = _('Deceased per 100k inhabitants')
            y_label = _('Deaths')
            for region in regions:                
                df_region = self._df[self._df.CCAA==region]
                x = df_region.index.get_level_values('fecha')
                df_region['deaths_per_100k'] = self._df['deceased'] * 100_000 / self._df['population']
                plt.plot(x, df_region['deaths_per_100k'])
                region_name = _(region)
                ax.annotate(f"{df_region['deaths_per_100k'][-1]:0,.0f} ({region_name})", xy=(x[-1]  - np.timedelta64(12,'h'), df_region['deaths_per_100k'][-1]))

        
        plt.title(title, fontsize=26)
        ax.set_ylabel(y_label,fontsize=15)
        ax.set_xlim(np.datetime64('2020-03-01'))
        ax.figure.autofmt_xdate()
        if legend:
            ax.legend(loc='upper left',fontsize=17)
        self._add_footer(ax)
        plt.savefig(image_path)
        plt.close()

    def _add_footer(self, ax):
        ax.set_xlabel(_('Generated by COVID19gram (telegram bot)\n Data source from Datadista (see https://github.com/datadista/datasets/)'),
              position=(1., 0.),
              fontproperties=self._footer_font,
              horizontalalignment='right')

    def _add_global_footer(self, ax):
        ax.set_xlabel(_('Generated by COVID19gram (telegram bot)\n Data source from covid19.health (see https://github.com/stevenliuyi/covid19/)'),
              position=(1., 0.),
              fontproperties=self._footer_font,
              horizontalalignment='right')
