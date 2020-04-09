#!/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
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

    SCOPES = [
        'spain',
        'world'
    ]

    _source_path = None
    _images_dir = None
    _footer_font = None
    # 'world' and 'spain'
    # each item will contain the dataframe (df), timestamp (ts)
    _sources = {}
    _translations = {}

    def __init__(self, data_directory='data', images_dir='images/'):
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        self._source_path = data_directory
        self._load_translations()
        for scope in self.SCOPES:
            self._reload_data(scope)
        self._images_dir = images_dir
        self._footer_font = FontProperties()
        self._footer_font.set_family('serif')
        self._footer_font.set_style('italic')

    def _reload_data(self, scope):
        csv_path = f"{self._source_path}/{scope}_cases.csv"
        if not os.path.isfile(csv_path):
            raise RuntimeError(f"Datasource {scope} not found ({csv_path})")

        df = pd.read_csv(csv_path)
        # convert date to datetime and set index
        df['fecha'] = pd.to_datetime(df['fecha'])
        df.set_index(['fecha', 'cod_ine'], inplace=True)
        df.rename(columns={'total': 'cases', 'CCAA': 'region'}, inplace=True)
        # column recovered
        rec_df = pd.read_csv(f"{self._source_path}/{scope}_recovered.csv")
        rec_df['fecha'] = pd.to_datetime(rec_df['fecha'])
        rec_df.set_index(['fecha', 'cod_ine'], inplace=True)
        rec_df.columns = ['CCAA_altas', 'recovered']
        df = df.merge(rec_df, left_index=True, right_index=True, how='left')
        df.drop(columns=['CCAA_altas'], inplace=True)
        # column deceased
        dec_df = pd.read_csv(f"{self._source_path}/{scope}_deceased.csv")
        dec_df['fecha'] = pd.to_datetime(dec_df['fecha'])
        dec_df.set_index(['fecha', 'cod_ine'], inplace=True)
        dec_df.columns = ['CCAA_fac', 'deceased']
        df = df.merge(dec_df, left_index=True, right_index=True, how='left')
        df.drop(columns=['CCAA_fac'], inplace=True)
        # column population
        if os.path.isfile(f"{self._source_path}/{scope}_population.csv"):
            pop_df = pd.read_csv(f"{self._source_path}/{scope}_population.csv")
            if scope == 'world':
                pop_df.set_index('country_name', inplace=True)
                df = df.merge(pop_df, left_on='region',
                              right_index=True, how='left')
            else:
                pop_df.set_index('cod_ine', inplace=True)
                df = df.merge(pop_df, left_index=True,
                              right_index=True, how='left')
        else:
            df['population'] = 0

        df.fillna(0, inplace=True)
        df.sort_index()

        df['cases_per_100k'] = df['cases'] * 100_000 / df['population']
        df['deceased_per_100k'] = df['deceased'] * 100_000 / df['population']
        df['active_cases'] = df['cases'] - df['recovered'] - df['deceased']

        source = self._sources.get(scope, {})
        source['df'] = df
        source['ts'] = int(os.path.getmtime(csv_path))
        self._sources[scope] = source

    def _check_new_data(self, scope):
        csv_path = f"{self._source_path}/{scope}_cases.csv"
        if not os.path.isfile(csv_path):
            raise RuntimeError(f"Datasource {scope} not found ({csv_path})")

        source = self._sources.get(scope, {})
        if int(os.path.getmtime(csv_path)) != source.get('ts'):
            self._reload_data(scope)

    def _load_translations(self):
        for language in self.LANGUAGES:
            translation = gettext.translation('messages', localedir='locales', languages=[language])
            translation.install()
            self._translations[language] = translation

    def get_regions(self, scope):
        source = self._sources.get(scope, {})
        df = source.get('df')
        return list(df.region.unique())

    def get_region_scope(self, region):
        region_scope = None
        for scope in self.SCOPES:
            if region in self.get_regions(scope):
                region_scope = scope
                break
        return region_scope

    def generate_plot(self, plot_type, region, language='en'):
        if plot_type not in self.PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        region_scope = self.get_region_scope(region)
        if not region_scope:
            raise RuntimeError(_('Region not found in any scope'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(region_scope)
        source = self._sources.get(region_scope)
        # check if image has already been generated
        image_fpath = f"{self._images_dir}/{language}_{region}_{plot_type}_{source.get('ts')}.png"
        if os.path.isfile(image_fpath):
            return image_fpath

        # get region data
        region_df = self._get_plot_data(plot_type, source.get('df'), region)
        self._plot(plot_type, region_scope, region, language, region_df, image_fpath)
        return image_fpath

    def generate_multiregion_plot(self, plot_type, regions, language='en'):
        if plot_type not in self.MULTIREGION_PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        if len(regions) == 0:
            raise RuntimeError(_('No regions given to generate a multiregion plot'))

        region_scope = self.get_region_scope(regions[0])
        if not region_scope:
            raise RuntimeError(_('First region not found in any scope'))

        for region in regions[1:]:
            if region not in self.get_regions(region_scope):
                raise RuntimeError(_("Region {region} not found in first region scope ({region_scope})".format(region=region, region_scope=region_scope)))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(region_scope)
        source = self._sources.get(region_scope)

        # check if image has already been generated
        region = '-'.join([region for region in sorted(regions)])
        image_fpath = f"{self._images_dir}/{language}_{region}_{plot_type}_{source.get('ts')}.png"
        if os.path.isfile(image_fpath):
            return image_fpath

        df = source.get('df')
        self._multiregion_plot(plot_type, region_scope, regions, language, df, image_fpath)
        return image_fpath

    def _get_plot_data(self, plot_type, df, region):
        region_df = df[df.region == region]
        if plot_type == 'daily_cases':
            # calculate daily increase and rolling avg
            region_df['increase'] = region_df['cases'] - region_df['cases'].shift(1)
            region_df['rolling'] = region_df.rolling(window=3).mean()['increase']
        elif plot_type == 'daily_deceased':
            # calculate daily increase and rolling avg
            region_df['increase'] = region_df['deceased'] - region_df['deceased'].shift(1)
            region_df['rolling'] = region_df.rolling(window=3).mean()['increase']
        return region_df

    def _plot(self, plot_type, scope, region, language, df, image_path):
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
            ax.annotate(f"{df['increase'][-1]:0,.0f}", xy=(x[-1], df['increase'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'daily_deceased':
            title = _('Daily deaths evolution at {region}').format(region=_(region))
            y_label = _('Deaths')
            plt.bar(x, df['increase'], alpha=0.5, width=0.9, color='red', label=_('Daily deaths'))
            plt.fill_between(x, 0, df['rolling'], color='red', alpha=0.2, label=_('Deaths rolling avg (3 days)'))
            plt.plot(x, df['rolling'], color='red')
            ax.annotate(f"{df['increase'][-1]:0,.0f}", xy=(x[-1], df['increase'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'active_recovered_deceased':
            title = _('Active cases, recovered and deceased at {region}').format(region=_(region))
            y_label = _('Cases')
            alpha = 0.3
            plt.fill_between(x, 0, df['active_cases'], alpha=alpha, label=_('Currently infected'))
            plt.plot(x, df['active_cases'])
            ax.annotate(f"{df['active_cases'][-1]:0,.0f}", xy=(x[-1], df['active_cases'][-1]),
                        xytext=(0, 3), textcoords="offset points")
            plt.fill_between(x, 0, df['recovered'], color='g', alpha=alpha, label=_('Recovered'))
            plt.plot(x, df['recovered'], color='g')
            ax.annotate(f"{df['recovered'][-1]:0,.0f}", xy=(x[-1], df['recovered'][-1]),
                        xytext=(0, 3), textcoords="offset points")
            plt.fill_between(x, 0, df['deceased'], color='red', alpha=alpha, label=_('Deceased'))
            plt.plot(x, df['deceased'], color='red')
            ax.annotate(f"{df['deceased'][-1]:0,.0f}", xy=(x[-1], df['deceased'][-1]),
                        xytext=(0, 3), textcoords="offset points")
        elif plot_type == 'active':
            title = _('Active cases at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['active_cases'], alpha=0.5, width=1, label=_('Active cases'))
            ax.annotate(f"{df['active_cases'][-1]:0,.0f}", xy=(x[-1], df['active_cases'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'recovered':
            title = _('Recovered cases at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['recovered'], alpha=0.5, width=1, color='g', label=_('Recovered cases'))
            ax.annotate(f"{df['recovered'][-1]:0,.0f}", xy=(x[-1], df['recovered'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'deceased':
            title = _('Deaths evolution at {region}').format(region=_(region))
            y_label = _('Deaths')
            plt.bar(x, df['deceased'], alpha=0.5, width=1, color='r', label=_('Deceased'))
            ax.annotate(f"{df['deceased'][-1]:0,.0f}", xy=(x[-1], df['deceased'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')
        elif plot_type == 'cases_normalized':
            title = _('Cases per 100k inhabitants at {region}').format(region=_(region))
            y_label = _('Cases')
            plt.bar(x, df['cases_per_100k'], alpha=0.5, width=1, label=_('Active cases'))
            ax.annotate(f"{df['cases_per_100k'][-1]:0,.0f}", xy=(x[-1], df['cases_per_100k'][-1]),
                        xytext=(0, 3), textcoords="offset points", ha='center')

        plt.title(title, fontsize=26)
        ax.set_ylabel(y_label, fontsize=15)
        xlim = self._get_plot_xlim(scope, df)
        if xlim:
            ax.set_xlim(xlim)
        ax.figure.autofmt_xdate()
        ax.legend(loc='upper left', fontsize=17)
        self._add_footer(ax, scope)
        plt.savefig(image_path)
        plt.close()

    def _multiregion_plot(self, plot_type, scope, regions, language, df, image_path):
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
                df_region = df[df.region == region]
                x = df_region.index.get_level_values('fecha')
                plt.plot(x, df_region['cases_per_100k'])
                region_name = _(region)
                ax.annotate(f"{df_region['cases_per_100k'][-1]:0,.0f} ({region_name})",
                            xy=(x[-1], df_region['cases_per_100k'][-1]), xytext=(0, 3),
                            textcoords="offset points")

        elif plot_type == 'deceased_normalized':
            legend = False
            title = _('Deceased per 100k inhabitants')
            y_label = _('Deaths')
            for region in regions:
                df_region = df[df.region == region]
                x = df_region.index.get_level_values('fecha')
                plt.plot(x, df_region['deceased_per_100k'])
                region_name = _(region)
                ax.annotate(f"{df_region['deceased_per_100k'][-1]:0,.0f} ({region_name})",
                            xy=(x[-1], df_region['deceased_per_100k'][-1]), xytext=(0, 3),
                            textcoords="offset points")

        plt.title(title, fontsize=26)
        ax.set_ylabel(y_label, fontsize=15)
        xlim = self._get_plot_xlim(scope, df)
        if xlim:
            ax.set_xlim(xlim)
        ax.figure.autofmt_xdate()
        if legend:
            ax.legend(loc='upper left', fontsize=17)
        self._add_footer(ax, scope)
        plt.savefig(image_path)
        plt.close()

    def _get_plot_xlim(self, scope, df):
        if scope == 'spain':
            return np.datetime64('2020-03-01')

        # if cases have reached at least 1000, show since it reached 100. Else, 5 cases
        max_cases = np.max(df['cases'])
        if max_cases > 1000:
            dates_gt_100 = df[df.cases > 100].index.get_level_values('fecha')
            return dates_gt_100[0]
        else:
            dates_gt_5 = df[df.cases > 5].index.get_level_values('fecha')
            if len(dates_gt_5) > 0:
                return dates_gt_5[0]
        return None

    def _add_footer(self, ax, scope):
        ds_credits = None
        if scope == 'spain':
            ds_name = 'Datadista'
            ds_url = "https://github.com/datadista/datasets/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})".format(ds_name=ds_name, ds_url=ds_url))
        else:
            ds_name = 'JHU CSSE'
            ds_url = "https://github.com/pomber/covid19"
            ds_credits = _("Data source from {ds_name} through Pomber's JSON API (see {ds_url})".format(ds_name=ds_name, ds_url=ds_url))

        ax.set_xlabel(
            _('Generated by COVID19gram (telegram bot)') + "\n" + ds_credits,
            position=(1., 0.),
            fontproperties=self._footer_font,
            horizontalalignment='right')
