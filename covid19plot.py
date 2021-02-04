#!/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
from gettext import gettext as _
import gettext
import locale

import matplotlib
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.font_manager import FontProperties
import seaborn as sns
import geopandas as gpd
from config.countries import countries
import pycountry
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import matplotlib.colors as colors
from collections import Counter

from plot_types.base import COVID19PlotTypeManager

sns.set_context("notebook")
sns.set_style("whitegrid")
matplotlib.use('Agg')


def cmap_discretize(cmap, N):
    """Return a discrete colormap from the continuous colormap cmap.
        cmap: colormap instance, eg. cm.jet.
        N: number of colors.
    """
    if type(cmap) == str:
        cmap = cm.get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0., 0., 0., 0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N + 1)
    cdict = {}
    for ki, key in enumerate(('red', 'green', 'blue')):
        cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki]) for i in range(N + 1)]
    # Return colormap object.
    return colors.LinearSegmentedColormap(cmap.name + "_%d" % N, cdict, 1024)


class COVID19Plot(object):

    LANGUAGES = ['ca', 'es', 'en', 'it']
    PLOT_TYPES = [
        'daily_cases',
        'daily_hospitalized',
        'active_recovered_deceased',
        'active',
        'cases',
        'hosp_normalized',
        # 'deceased',
        # 'recovered',
        'reproduction_rate',
        'daily_deceased',
        'consolidation_acum14',
        # 'cases_normalized',
    ]

    MULTIREGION_PLOT_TYPES = [
        'cases',
        'acum14_cases_normalized',
        'acum14_hospitalized_normalized',
        'cases_logarithmic',
        'cases_normalized',
        'hospitalized',
        'hospitalized_logarithmic',
        'hospitalized_normalized',
        'deceased_normalized',
    ]

    SCOPE_PLOT_TYPES = [
        'cases',
        'hospitalized',
        'cases_normalized',
        'cases_normalized_heatmap',
        'deceased_normalized_heatmap',
        'cases_heatmap',
        'active_cases_heatmap',
        'active_cases_normalized_heatmap',
        'increase_cases_normalized_heatmap',
        'acum14_deceased_normalized_heatmap',
        'acum14_cases_normalized_heatmap',
        'acum14_hosp_normalized_heatmap',
        'hosp_normalized',
        'daily_cases_normalized',
        'deceased_normalized',
        'daily_deceased_normalized',
        'daily_deceased_normalized',
        'map',
    ]

    BUTTON_PLOT_TYPES = [
        'daily_cases',
        'active_recovered_deceased',
        'cases',
        'reproduction_rate',
        'daily_deceased',
    ]

    BUTTON_SCOPE_PLOT_TYPES = [
        'cases',
        'acum14_cases_normalized_heatmap',
        'increase_cases_normalized_heatmap',
        'deceased_normalized_heatmap',
        'acum14_deceased_normalized_heatmap'
    ]

    SCOPES = [
        'spain',
        'italy',
        'france',
        'austria',
        'argentina',
        'australia',
        'brazil',
        'canada',
        'chile',
        'china',
        'colombia',
        'germany',
        'india',
        'mexico',
        'portugal',
        'us',
        'unitedkingdom',
        'world',
        'balears',
        'mallorca',
        'menorca',
        'eivissa',
        'catalunya'
    ]

    AGES = [
    ]

    CB_color_cycle = [
        '#377eb8', '#ff7f00', '#4daf4a',
        '#f781bf', '#a65628', '#984ea3',
        '#999999', '#e41a1c', '#dede00'
    ]

    grey_cycle = ['#7d755b', '#8d8670', '#9e9884', '#aea998', '#bebaad', '#cecbc1', '#dfdcd6', '#efeeea']

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
        csv_path = f"{self._source_path}/{scope}_covid19gram.csv"
        if not os.path.isfile(csv_path):
            raise RuntimeError(f"Datasource {scope} not found ({csv_path})")

        df = pd.read_csv(csv_path)
        # convert date to datetime and set index
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date', 'region_code'], inplace=True)
        df.sort_index()
        source = self._sources.get(scope, {})
        source['df'] = df
        source['ts'] = int(os.path.getmtime(csv_path))
        if scope in self.AGES:
            csv_path = f"{self._source_path}/{scope}_ages.csv"
            if not os.path.isfile(csv_path):
                raise RuntimeError(f"Datasource {scope}(Ages) not found ({csv_path})")
            df_ages = pd.read_csv(csv_path, encoding='utf-8-sig')
            df_ages['date'] = pd.to_datetime(df_ages['fecha'])
            df_ages.set_index(['date'], inplace=True)
            df_ages.sort_index(ascending=True)
            source['df_ages'] = df_ages
            # source['ts_ages'] = int(os.path.getmtime(csv_path))
        self._sources[scope] = source

    def _check_new_data(self, scope):
        csv_path = f"{self._source_path}/{scope}_covid19gram.csv"
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

    def expand_scope(self, scope):
        names = {
            'gl': 'world',
            'es': 'spain',
            'it': 'italy',
            'fr': 'france',
            'at': 'austria',
            'ar': 'argentina',
            'au': 'australia',
            'br': 'brazil',
            'ca': 'canada',
            'cl': 'chile',
            'cn': 'china',
            'co': 'colombia',
            'de': 'germany',
            'in': 'india',
            'mx': 'mexico',
            'pt': 'portugal',
            'us': 'us',
            'gb': 'unitedkingdom',
            'ib': 'balears',
            'ma': 'mallorca',
            'me': 'menorca',
            'ei': 'eivissa',
            'ct': 'catalunya',
            'vd': 'void',
        }
        if scope in names:
            return names[scope]
        return None

    def zip_scope(self, scope):
        names = {
            'world': 'gl',
            'spain': 'es',
            'italy': 'it',
            'france': 'fr',
            'austria': 'at',
            'argentina': 'ar',
            'australia': 'au',
            'brazil': 'br',
            'canada': 'ca',
            'chile': 'cl',
            'china': 'cn',
            'colombia': 'co',
            'germany': 'de',
            'india': 'in',
            'mexico': 'mx',
            'portugal': 'pt',
            'us': 'us',
            'unitedkingdom': 'gb',
            'balears': 'ib',
            'mallorca': 'ma',
            'menorca': 'me',
            'eivissa': 'ei',
            'catalunya': 'ct',
            'void': 'vd'
        }

        if scope in names:
            return names[scope]

    def _only_consolidated(self, df):
        correction = 0.05
        while df['increase_cases'][-1] == 0 and int(correction * df['rolling_cases'][-1]) > int(df['increase_cases'][-1]):
            df = df.iloc[:-1]
        return df

    def get_region_scope(self, region):
        region_scope = None
        for scope in self.SCOPES:
            if region in self.get_regions(scope):
                region_scope = scope
                break
        return region_scope

    def has_region_scope(self, region, scope):
        if scope == 'void':
            scope = self.get_region_scope(region)
        if region in self.get_regions(scope):
            return True
        return False

    def get_summary(self, region, scope, language='en'):

        if scope == 'void':
            scope = self.get_region_scope(region)
            if not scope:
                raise RuntimeError(_('Region not found in any scope'))
        elif not self.has_region_scope(region, scope):
            raise RuntimeError(_('Region not found in scope'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(scope)
        source = self._sources.get(scope)

        # get region data
        region_df = self._get_plot_data('summary', source.get('df'), region)
        caption = self._get_caption('summary', scope, region, language, region_df)
        return caption

    def get_plot_caption(self, plot_type, region, scope, language='en'):
        if plot_type not in self.PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        if scope == 'void':
            scope = self.get_region_scope(region)
            if not scope:
                raise RuntimeError(_('Region not found in any scope'))
        elif not self.has_region_scope(region, scope):
            raise RuntimeError(_('Region not found in scope'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(scope)
        source = self._sources.get(scope)
        if plot_type == 'active_recovered_deceased' and region == f"total-{scope}" and scope in self.AGES:
            plot_type = 'ages'
        if region != 'total-france' and scope == 'france':
            if plot_type == 'reproduction_rate':
                plot_type = 'recovered'
            if plot_type == 'cases':
                plot_type = 'hospitalized'
        PlotTypeCls = COVID19PlotTypeManager.get_plot_type(plot_type)
        if PlotTypeCls is None:
            raise RuntimeError(_('Plot type is not recognized'))

        translation = self._translations[language].gettext
        self._set_locale(language)

        # get region data
        if plot_type == 'ages':
            region_df = self._get_ages_df(scope, total=True)
        else:
            region_df = self._get_plot_data(plot_type, source.get('df'), region)
        region_plot = PlotTypeCls(scope, region, region_df, translation)
        caption = region_plot.get_caption()
        return caption

    def get_scope_plot_caption(self, plot_type, scope, language='en'):
        if plot_type not in self.SCOPE_PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(scope)
        source = self._sources.get(scope)

        # get region data
        df = source.get('df')
        caption = self._get_scope_caption(plot_type, scope, language, df)
        return caption

    def generate_plot(self, plot_type, region, scope, language='en', force=False):
        if plot_type not in self.PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        if scope == 'void':
            scope = self.get_region_scope(region)
            if not scope:
                raise RuntimeError(_('Region not found in any scope'))
        elif not self.has_region_scope(region, scope):
            raise RuntimeError(_('Region not found in scope'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(scope)
        source = self._sources.get(scope)
        image_fpath = None

        # check if image has already been generated
        if plot_type == 'active_recovered_deceased' and region == f"total-{scope}" and scope in self.AGES:
            image_fpath = f"{self._images_dir}/{language}_{region}_ages_{source.get('ts')}.png"
            plot_type = 'ages'
        else:
            image_fpath = f"{self._images_dir}/{language}_{region}_{plot_type}_{source.get('ts')}.png"
        if os.path.isfile(image_fpath) and not force:
            return image_fpath

        if region != 'total-france' and scope == 'france':
            if plot_type == 'reproduction_rate':
                plot_type = 'recovered'
            if plot_type == 'cases':
                plot_type = 'hospitalized'

        # get region data
        if plot_type == 'ages':
            region_df = self._get_ages_df(scope)
        else:
            region_df = self._get_plot_data(plot_type, source.get('df'), region)
        PlotTypeCls = COVID19PlotTypeManager.get_plot_type(plot_type)
        if PlotTypeCls is None:
            raise RuntimeError(_('Plot type is not recognized'))

        if 'acum14_cases' in plot_type or 'acum14_deceased' in plot_type or 'reproduction_rate' in plot_type:
            l_date = region_df.index.get_level_values('date')[-1]
            f_date = region_df['acum14_cases'].idxmin()[0]
            region_df = region_df.loc[f_date:l_date]

        if scope in ['balears', 'mallorca', 'menorca', 'eivissa'] and "deceased" in plot_type:
            l_date = region_df['deceased'].notna()[::-1].idxmax()[0].strftime("%Y-%m-%d")
            region_df = region_df.loc['2020-10-08':l_date]

        translation = self._translations[language].gettext
        self._set_locale(language)
        region_plot = PlotTypeCls(scope, region, region_df, translation)
        region_plot.plot(image_fpath)
        return image_fpath

    def generate_multiregion_plot(self, plot_type, regions, scope, language='en', force=False):
        if plot_type not in self.MULTIREGION_PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        if len(regions) == 0:
            raise RuntimeError(_('No regions given to generate a multiregion plot'))

        if not self.has_region_scope(regions[0], scope):
            raise RuntimeError(_('First region not found in scope'))

        for region in regions[1:]:
            if region not in self.get_regions(scope):
                raise RuntimeError(_("Region {region} not found in first region scope ({scope})".format(region=region, scope=scope)))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(scope)
        source = self._sources.get(scope)

        # check if image has already been generated
        region = '-'.join([region for region in sorted(regions)])
        image_fpath = f"{self._images_dir}/{language}_{region}_{plot_type}_{source.get('ts')}.png"
        if os.path.isfile(image_fpath) and not force:
            return image_fpath

        df = source.get('df')

        if scope == 'france' and plot_type == 'acum14_cases_normalized':
            plot_type = 'acum14_hospitalized_normalized'

        PlotTypeCls = COVID19PlotTypeManager.get_plot_type(f'm_{plot_type}')
        if PlotTypeCls is None:
            raise RuntimeError(_('Plot type is not recognized'))

        if scope in ['balears', 'mallorca', 'menorca', 'eivissa'] and "deceased" in plot_type:
            l_date = df['deceased'].notna()[::-1].idxmax()[0].strftime("%Y-%m-%d")
            df = df.loc['2020-10-08':l_date]

        if 'acum14_cases' in plot_type or 'acum14_deceased' in plot_type or 'reproduction_rate' in plot_type:
            l_date = df['acum14_cases'].index.get_level_values('date')[-1]
            f_date = df['acum14_cases'].idxmin()[0]
            df = df.loc[f_date:l_date]

        translation = self._translations[language].gettext
        self._set_locale(language)
        region_plot = PlotTypeCls(scope, regions, df, translation)
        region_plot.plot(image_fpath)
        return image_fpath

    def generate_scope_plot(self, plot_type, scope, language='en', force=False):
        if plot_type not in self.SCOPE_PLOT_TYPES:
            raise RuntimeError(_('Plot type is not recognized'))

        # check if data source has been modified, and reload it if necessary
        self._check_new_data(scope)
        source = self._sources.get(scope)
        # check if image has already been generated
        image_fpath = f"{self._images_dir}/{language}_{scope}_{plot_type}_{source.get('ts')}.png"
        if os.path.isfile(image_fpath) and not force:
            return image_fpath

        # get region data
        df = source.get('df')

        if scope in ['balears', 'mallorca', 'menorca', 'eivissa'] and "deceased" in plot_type:
            l_date = df['deceased'].notna()[::-1].idxmax()[0].strftime("%Y-%m-%d")
            df = df.loc['2020-10-08':l_date]

        if 'acum14_cases' in plot_type or 'acum14_deceased' in plot_type or 'reproduction_rate' in plot_type:
            l_date = df.index.get_level_values('date')[-1]
            f_date = df['acum14_cases'].idxmin()[0]
            df = df.loc[f_date:l_date]
        self._scope_plot(plot_type, scope, language, df, image_fpath)
        return image_fpath

    def _get_plot_data(self, plot_type, df, region):
        region_df = df[df.region == region]
        return region_df

    def _get_caption(self, plot_type, scope, region, language, df):
        _ = self._translations[language].gettext
        self._set_locale(language)
        last_data = None
        last_date = df.index.get_level_values('date')[-1].strftime("%d/%B/%Y")

        if plot_type == 'summary':
            v = locale.format_string('%.0f', df['cases'][-1], grouping=True).replace('nan', '-')
            last_data = "  🦠 " + _('Total cases') + ": `" + v
            v = locale.format_string('%+.0f', df['increase_cases'][-1], grouping=True).replace('nan', '-')
            last_data += " (" + v + ")`\n"
            v = locale.format_string(
                '%.1f', df['cases_per_100k'][-1], grouping=True).replace('nan', '-')
            last_data += "    `" + v + "` __" + _('per 100k inhabitants') + "__\n\n"
            v = locale.format_string('%.0f', df['deceased'][-1], grouping=True).replace('nan', '-')
            last_data += "  ❌ " + _('Total deceased') + ": `" + v
            v = locale.format_string('%+.0f', df['increase_deceased'][-1], grouping=True).replace('nan', '-')
            last_data += " (" + v + ")`\n"
            v = locale.format_string(
                '%.1f', df['deceased_per_100k'][-1], grouping=True).replace('nan', '-')
            last_data += "    `" + v + "` __" + _('per 100k inhabitants') + "__\n\n"
            v = locale.format_string(
                '%.0f', df['recovered'][-1], grouping=True).replace('nan', '-')
            last_data += "  ✅ " + _('Recovered') + ": `" + v + "`\n\n"
            v = locale.format_string('%.0f', df['active_cases'][-1], grouping=True).replace('nan', '-')
            last_data += "  😷 " + _('Active') + ": `" + v + "`\n\n"
            rt = -1
            v = locale.format_string('%.2f', df['Rt'][rt], grouping=True).replace('nan', '-')
            last_data += "  👩‍👦‍👦 " + _('Reproduction Rate') + ": `" + v + "`\n"

        updated = "\n" + _("Information on last available data") + " (" + last_date + ")."
        note_Spain = ""
        if scope == 'spain' and plot_type == "reproduction_rate":
            note_Spain = "\n" + _("Check CI14 per 100k consolidation using 🚧")
        if scope == 'spain':
            note_Spain += "\n" + _("Spain's data may take a few days to be consolidated and may be incomplete") + "‼️"
        return f"{last_data}\n__{updated}____{note_Spain}__"

    def _scope_plot(self, plot_type, scope, language, df, image_path):
        # set translation to current language
        _ = self._translations[language].gettext
        self._set_locale(language)
        title = None
        legend = False
        color = 'b'
        label = _('Cases')
        last_date = df.index.get_level_values('date')[-1]

        if plot_type == 'cases_normalized':
            title = _('Cases per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
            field = 'cases_per_100k'
            if scope == 'france':
                title = _('Hospitalizations per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
                field = 'hosp_per_100k'
                color = 'goldenrod'
        elif plot_type == 'cases':
            title = _('Cases') + f" ({last_date:%d/%B/%Y})"
            field = 'cases'
            color = 'dodgerblue'
            if scope == 'france':
                title = _('Currently hospitalized') + f" ({last_date:%d/%B/%Y})"
                field = 'hospitalized'
                color = 'goldenrod'
        elif plot_type == 'cases_heatmap':
            title = _('Cases')
            field = 'cases'
        elif plot_type == 'cases_normalized_heatmap':
            title = _('Cases per 100k inhabitants')
            field = 'cases_per_100k'
        elif plot_type == 'active_cases_heatmap':
            title = _('Active cases')
            field = 'active_cases'
        elif plot_type == 'active_cases_normalized_heatmap':
            title = _('Active cases per 100k inhabitants')
            field = 'active_cases_per_100k'
        elif plot_type == 'deceased_normalized_heatmap':
            title = _('Deceased per 100k inhabitants')
            field = 'deceased_per_100k'
        elif plot_type == 'increase_cases_normalized_heatmap':
            title = _('New daily cases per 100k inhabitants')
            field = 'increase_cases_per_100k'
        elif plot_type == 'acum14_deceased_normalized_heatmap':
            title = _('Cumulative incidence of deceased (14 days/100k inhabitants)')
            field = 'acum14_deceased_per_100k'
        elif plot_type == 'acum14_cases_normalized_heatmap':
            title = _('Cumulative incidence (14 days/100k inhabitants)')
            field = 'acum14_cases_per_100k'
            if scope == 'france':
                title = _('Cumulative incidence of hospitalizations (14 days/100k inhabitants)')
                field = 'acum14_hosp_per_100k'
        elif plot_type == 'acum14_hosp_normalized_heatmap':
            title = _('Cumulative incidence of hospitalizations (14 days/100k inhabitants)')
            field = 'acum14_hosp_per_100k'
        elif plot_type == 'hospitalized':
            title = _('Hospitalizations') + f" ({last_date:%d/%B/%Y})"
            field = 'hospitalized'
            color = 'goldenrod'
        elif plot_type == 'deceased_normalized':
            title = _('Deceased per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
            field = 'deceased_per_100k'
            color = 'r'
        elif plot_type == 'daily_cases_normalized':
            title = _('New cases per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
            field = 'rolling_cases_per_100k'
            if scope == 'france':
                title = _('New hospitalizations per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
                field = 'rolling_hosp_per_100k'
                color = 'goldenrod'
            legend = True
            label = _('Increment rolling avg (7 days)')
        elif plot_type == 'daily_deceased_normalized':
            title = _('New deceased per 100k inhabitants') + f" ({last_date:%d/%B/%Y})"
            field = 'rolling_deceased_per_100k'
            legend = True
            color = 'r'
            label = _('Increment rolling avg (7 days)')

        elif plot_type == 'map':
            cmap_name = 'Blues'
            field = 'acum14_cases_per_100k'
            title = _('Cumulative incidence (14 days/100k inhabitants)')
            if scope == 'france':
                field = 'acum14_hosp_per_100k'
                title = _('Cumulative incidence of hospitalizations (14 days/100k inhabitants)')
                cmap_name = 'Oranges'
            self._get_map_plot(field, scope, cmap_name, title, language, df, image_path)
            return

        fig, ax = plt.subplots(figsize=(12, 8))

        if 'heatmap' in plot_type:
            last_date = df.index.get_level_values('date')[-1]
            dates = df.index.get_level_values(0)
            last_15days = last_date - np.timedelta64(15, 'D')
            plot_df = df[dates >= last_15days]
            if scope == 'world':
                today_df = plot_df.loc[last_date]
                today_df = today_df[(today_df.cases > 1000) & (today_df.region != 'total-world')]
                plot_df = plot_df[plot_df.region.isin(today_df.region.unique())]

            plot_df = plot_df.reset_index()[['date', 'region', field]]
            if 'normalized' not in plot_type:
                total_region = f"total-{scope}"
                plot_df = plot_df[plot_df.region != total_region]

            pivot = plot_df.pivot("region", "date", field)
            pivot = pivot.sort_values(last_date, ascending=False).head(20)
            dates = pd.to_datetime(pivot.columns.values)
            cmap = 'Blues'
            if 'deceased' in field:
                cmap = "Reds"
            elif 'hosp' in field:
                cmap = "Oranges"
            palette = sns.color_palette(cmap, 20)
            vmax = pivot.quantile(0.7, axis=1).max()
            fmt = "0.0f"
            if vmax < 50:
                fmt = "0.1f"
            ax = sns.heatmap(pivot, cmap=palette, annot=True, fmt=fmt,
                             annot_kws=dict(fontsize=10),
                             yticklabels=[_(region) for region in pivot.index],
                             vmin=0, vmax=vmax)

            def each3_date_fmt(x, pos):
                if pos % 3 == 0:
                    return dates[pos].strftime("%d %b")
                return ""
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(each3_date_fmt))
            ax.set_ylabel('')
            ax.set_xlabel('')
            plt.xticks(rotation=45, ha='center', fontsize=12, color="#555555")
            ax.tick_params(axis='x', which='major', pad=0)
            plt.yticks(fontsize=12, color="#555555")
        else:
            today_df = df.loc[last_date]
            top_df = self._get_scope_df(plot_type, scope, today_df, field)

            ax.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
            regions = [_(region) for region in top_df['region']]
            plt.barh(y=regions, width=top_df[field], alpha=0.4, color=color, label=label)
            for region in top_df['region'].unique():
                value = top_df[top_df.region == region][field].values[0]
                fmt = '%.1f'
                if plot_type == 'cases':
                    fmt = '%.0f'
                value_f = locale.format_string(fmt, value, grouping=True).replace('nan', '-')
                ax.annotate(value_f, xy=(value, _(region)),
                            xytext=(3, 0),
                            textcoords="offset points", va='center')

            if plot_type != 'cases':
                if scope != 'world' and scope != 'france':
                    total_region = f"total-{scope}"
                    total_value = today_df[today_df.region == total_region][field].values[0]
                    ax.axvline(total_value, color=color, alpha=0.5)
                    total_value_f = locale.format_string('%.1f', total_value, grouping=True).replace('nan', '-')
                    ax.annotate(_("National average") + ": " + total_value_f, xy=(total_value, 0),
                                xytext=(3, -20),
                                textcoords="offset points", va='center')

                elif scope == 'world':
                    ax.annotate(_("Countries with more than 1,000 cases"), xy=(1, 0), xycoords='axes fraction',
                                xytext=(-20, 20), textcoords='offset pixels',
                                horizontalalignment='right',
                                verticalalignment='bottom')

        plt.title(title, fontsize=20)
        if legend:
            ax.legend(loc='center right', fontsize=10)
        self._add_footer(ax, scope, language)

        plt.tight_layout()
        plt.savefig(image_path)
        plt.close()

    def _get_scope_caption(self, plot_type, scope, language, df):
        _ = self._translations[language].gettext
        self._set_locale(language)

        last_date = df.index.get_level_values('date')[-1]
        title = None
        field = None
        plot_type = plot_type.replace('_heatmap', '')
        if scope == 'france':
            if plot_type == 'acum14_cases_normalized':
                plot_type = 'acum14_hosp_normalized'

        if plot_type == 'cases_normalized':
            title = _('Cases per 100k inhabitants')
            field = 'cases_per_100k'
            if scope == 'france':
                title = _('Hospitalizations per 100k inhabitants')
                field = 'hosp_per_100k'
        elif plot_type == 'cases':
            title = _('Cases')
            field = 'cases'
            if scope == 'france':
                field = 'hospitalized'
        elif plot_type == 'deceased_normalized':
            title = _('Deceased per 100k inhabitants')
            field = 'deceased_per_100k'
        elif plot_type == 'daily_cases_normalized':
            title = _('New cases per 100k inhabitants')
            field = 'rolling_cases_per_100k'
            if scope == 'france':
                title = _('New hospitalizations per 100k inhabitants')
                field = 'rolling_hosp_per_100k'
        elif plot_type == 'daily_deceased_normalized':
            title = _('New deceased per 100k inhabitants')
            field = 'rolling_deceased_per_100k'
        elif plot_type == 'active_cases':
            title = _('Active cases')
            field = 'active_cases'
        elif plot_type == 'active_cases_normalized':
            title = _('Active cases per 100k inhabitants')
            field = 'active_cases_per_100k'
        elif plot_type == 'increase_cases_normalized':
            title = _('New daily cases per 100k inhabitants')
            field = 'increase_cases_per_100k'
        elif plot_type == 'acum14_deceased_normalized':
            title = _('Cumulative incidence of deceased (14 days/100k inhabitants)')
            field = 'acum14_deceased_per_100k'
        elif plot_type == 'acum14_cases_normalized':
            title = _('Cumulative incidence (14 days/100k inhabitants)')
            field = 'acum14_cases_per_100k'
        elif plot_type == 'acum14_hosp_normalized':
            title = _('Cumulative incidence of hospitalizations (14 days/100k inhabitants)')
            field = 'acum14_hosp_per_100k'
        else:
            return ""
        today_df = df.loc[last_date]
        top_df = self._get_scope_df(plot_type, scope, today_df, field, max_records=5)
        top_df = top_df.sort_values(field, ascending=False)

        last_data = ""
        last_date = last_date.strftime("%d/%B/%Y")

        for region in top_df['region'].unique():
            value = top_df[top_df.region == region][field].values[0]
            fmt = '%.1f'
            if plot_type == 'cases':
                fmt = '%.0f'
            value_f = locale.format_string(fmt, value, grouping=True).replace('nan', '-')
            last_data = last_data + " - " + _(region) + ": " + value_f + "\n"
        updated = _("Information on last available data") + " (" + last_date + ")."
        note_Spain = ""
        if scope == 'spain':
            note_Spain = "\n" + _("Spain's data may take a few days to be consolidated and may be incomplete")
        return f"**{title}**\n\n{last_data}\n__{updated}____{note_Spain}__"

    def _get_scope_df(self, plot_type, scope, today_df, field, max_records=20):
        total_region = f"total-{scope}"
        top_df = today_df[today_df.region != total_region]
        if scope == 'world':
            top_df = top_df[today_df.cases > 1000]
        top_df = top_df.sort_values(field, ascending=True)
        top_df = top_df.tail(max_records)
        return top_df

    def _get_ages_df(self, scope, sex=None, total=False):
        source = self._sources.get(scope)
        df = source.get('df_ages')
        last_date = df.index.get_level_values('date')[-1]
        today_df = df.loc[last_date]
        if sex:
            today_df = today_df[today_df['sexo'] == sex]
        if not total:
            today_df = today_df[today_df['rango_edad'] != "Total"]
        return today_df

    def _get_plot_xlim(self, scope, df):
        if scope in ['spain', 'italy']:
            return np.datetime64('2020-03-01')

        # if cases have reached at least 1000, show since it reached 100. Else, 5 cases
        max_cases = np.max(df['cases'])
        if max_cases > 1000:
            dates_gt_100 = df[df.cases > 100].index.get_level_values('date')
            return dates_gt_100[0]
        else:
            dates_gt_5 = df[df.cases > 5].index.get_level_values('date')
            if len(dates_gt_5) > 0:
                return dates_gt_5[0]
        return None

    def _add_footer(self, ax, scope, language):
        # set translation to current language
        _ = self._translations[language].gettext

        ds_credits = ""
        if scope == 'spain':
            ds_name = 'Datadista'
            ds_url = "https://github.com/datadista/datasets/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif scope == 'world':
            ds_name = 'JHU CSSE'
            ds_url = "https://github.com/pomber/covid19"
            ds_credits = _("Data source from {ds_name} through Pomber's JSON API (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif scope == 'austria':
            ds_name = 'covid-data-austria'
            ds_url = "https://github.com/Daniel-Breuss/covid-data-austria"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif scope == 'italy':
            ds_name = 'Ministero della Salute (Italia)'
            ds_url = "https://github.com/pcm-dpc/COVID-19"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif scope == 'france':
            ds_name = 'OpenCOVID19-fr'
            ds_url = "https://opencovid19.fr/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif scope in ['balears', 'mallorca', 'menorca', 'eivissa']:
            ds_name = _('www.caib.cat through Covid_ib repository')
            ds_url = 'https://github.com/jaumeperello/covid_ib'
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        else:
            ds_name = 'Proyecto COVID-19'
            ds_url = "https://covid19tracking.narrativa.com/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)

        ax.set_xlabel(
            _('Generated by COVID19gram (telegram bot)') + "\n" + ds_credits,
            position=(1., 0.),
            fontproperties=self._footer_font,
            horizontalalignment='right')

    def _set_locale(self, language):
        try:
            if language == 'es':
                locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
                locale.setlocale(locale.LC_NUMERIC, "es_ES.UTF-8")
            elif language == 'ca':
                locale.setlocale(locale.LC_TIME, "ca_ES.UTF-8")
                locale.setlocale(locale.LC_NUMERIC, "es_ES.UTF-8")
            elif language == 'en':
                locale.setlocale(locale.LC_TIME, "en_GB.UTF-8")
                locale.setlocale(locale.LC_NUMERIC, "en_GB.UTF-8")
            elif language == 'it':
                locale.setlocale(locale.LC_TIME, "it_IT.UTF-8")
                locale.setlocale(locale.LC_NUMERIC, "it_IT.UTF-8")
        except locale.Error:
            pass

    def _get_map_plot(self, field, scope, cmap_name, title, language, df, image_path, maps_directory='maps'):
        # set translation to current language
        _ = self._translations[language].gettext
        self._set_locale(language)
        if scope in self.SCOPES:
            ticks = 10
            proj = {'world': 'EPSG:4326', 'us': 'EPSG:2955', 'spain': 'EPSG:3395', 'germany': 'EPSG:3395', 'mexico': "EPSG:2955", 'unitedkingdom': 'EPSG:3395', 'argentina': 'EPSG:3395', 'brazil': 'EPSG:3395', 'italy': 'EPSG:3395', 'france': 'EPSG:3395', 'austria': 'EPSG:3395', 'australia': 'EPSG:3395', 'canada': 'EPSG:2955', 'chile': 'EPSG:3395', 'colombia': 'EPSG:3395', 'china': 'EPSG:3395', 'portugal': 'EPSG:3395', 'india': 'EPSG:3395', 'balears': 'EPSG:3395', 'mallorca': 'EPSG:3395', 'menorca': 'EPSG:3395', 'eivissa': 'EPSG:3395', 'catalunya': 'EPSG:3395'}

            regions_df = df[(df.region != f'total-{scope}')]
            regions_df = regions_df.reset_index()[['date', 'region', field]]
            regions_df.set_index(['date'], inplace=True)
            last_date = regions_df.index.get_level_values('date')[-1]
            today_df = regions_df.loc[last_date]
            today_df = today_df[today_df.region.isin(today_df.region.unique())]

            # Add regions without today's data
            regions = Counter(df['region'].unique())
            today_regions = Counter(today_df['region'].unique())
            for region in regions - today_regions:
                if region != f'total-{scope}':
                    today_df = today_df.append({'region': region, field: float('NaN')}, ignore_index=True)

            # Missing regions Fix
            if scope == 'canada':
                today_df = today_df.append({'region': 'Nunavut', field: float('NaN')}, ignore_index=True)
                today_df = today_df.append({'region': 'Yukon', field: float('NaN')}, ignore_index=True)

            if scope == 'colombia':
                today_df = today_df.append({'region': 'Guaviare', field: float('NaN')}, ignore_index=True)

            if scope == 'india':
                today_df = today_df.append({'region': 'Lakshadweep', field: float('NaN')}, ignore_index=True)

            # Convert alpha_2 country codes to alpha_3 to match Wolrd shapefile codes.
            if scope == 'world':
                today_df['alpha_3'] = None
                for region in today_df['region']:
                    # Avoid codes that aren't in alpha_3 codes
                    if countries[region]['code'] not in ['DMP', 'MSZ', 'XK']:
                        alpha_3 = pycountry.countries.get(alpha_2=countries[region]['code']).alpha_3
                        today_df['alpha_3'].mask(today_df.region == region, alpha_3, inplace=True)

            shapefile = f'{maps_directory}/{scope}/{scope}.shp'
            gdf = gpd.read_file(shapefile)[['name', 'geometry']]

            gdf = gdf.to_crs(proj[scope])

            # Missing regions?
            # regions = Counter(gdf['name'].unique())
            # today_regions = Counter(today_df['region'].unique())
            # print(regions - today_regions)

            right_on = 'region'
            if scope == 'world':
                right_on = 'alpha_3'
            merged = gdf.merge(today_df, left_on='name', right_on=right_on)

            figsize = (12, 8)
            base_cmap = cm.get_cmap(cmap_name)
            cmap = cmap_discretize(base_cmap, ticks)

            pivot = merged
            pivot = pivot.sort_values(by=field, ascending=False).head(ticks)
            pvt = 0.8
            if scope == 'world':
                pvt = 0.6
            vmax = pivot.quantile(pvt, axis=0).max()
            units = 100
            if vmax <= 80:
                units = 10
            elif vmax <= 150:
                units = 20
            elif vmax <= 300:
                units = 50
            vmax -= vmax % - units
            if merged.isnull().any().any():
                ax = merged.plot(column=field, cmap=cmap, figsize=figsize, vmax=vmax, vmin=0, legend=False, edgecolor='lightsteelblue', missing_kwds={"color": "grey", },)
            else:
                ax = merged.plot(column=field, cmap=cmap, figsize=figsize, vmax=vmax, vmin=0, legend=False, edgecolor='lightsteelblue',)
            ax.set_xticks([])
            ax.set_yticks([])
            suptitle = scope.capitalize()
            suptitle = _(scope)
            # country name fix
            if scope == 'unitedkingdom':
                suptitle = _('United Kingdom')
            if scope == 'us':
                suptitle = _('US')
            plt.figtext(0.50, 0.94, suptitle, fontsize=30, weight='bold', color='grey', ha='center')
            plt.figtext(0.50, 0.90, title, fontsize=14, ha='center', color='grey')

            norm = Normalize(vmin=0, vmax=vmax)
            n_cmap = cm.ScalarMappable(norm=norm, cmap=cmap)
            n_cmap.set_array([])
            cbar = ax.get_figure().colorbar(n_cmap, orientation='horizontal', aspect=30)
            lng = vmax // ticks
            tks_list = [i * lng for i in range(0, int((vmax // lng) + 1))]
            labels = [str(int(i * lng)) for i in range(0, int((vmax // lng) + 1))]
            labels[-1] = ">" + labels[-1]
            cbar.set_ticks(tks_list)
            cbar.ax.set_xticklabels(labels)

            plt.axis('off')

            plt.savefig(image_path)
            plt.close()
