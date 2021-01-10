import abc
import locale
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties


class COVID19PlotTypeManager(object):
    plot_types = []

    @staticmethod
    def register_plot_type(plot_type):
        COVID19PlotTypeManager.plot_types.append(plot_type)

    @staticmethod
    def get_plot_types():
        return [Plot_type.get_name() for Plot_type in COVID19PlotTypeManager.plot_types]

    @staticmethod
    def get_plot_type(name):
        for Plot_type in COVID19PlotTypeManager.plot_types:
            if Plot_type.get_name() == name:
                return Plot_type
        return None


class COVID19PlotType(object):

    __metaclass__ = abc.ABCMeta
    _name = None
    _category = None

    def __init__(self, scope, region, df, translation):
        self.scope = scope
        self.region = region
        self.translation = translation
        self.df = df

    @classmethod
    def get_name(cls):
        return cls._name

    @classmethod
    def get_category(cls):
        return cls._category

    @abc.abstractmethod
    def get_title(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_y_label(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_fields(self):
        raise NotImplementedError

    def plot(self, image_path=None):
        _ = self.translation
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        self._plot_data(plt, ax)
        plt.title(self.get_title(), fontsize=26)
        ax.set_ylabel(self.get_y_label(), fontsize=15)
        xlim = self._get_plot_xlim()
        if xlim:
            ax.set_xlim(xlim)
        ax.figure.autofmt_xdate()
        if self.get_category() == 'multiregion':
            ax.legend(loc='upper left', fontsize=17)
        self._add_footer(ax)
        if image_path:
            plt.savefig(image_path)
        else:
            plt.show()
        plt.close()

    def get_caption(self):
        _ = self.translation
        last_data = ""
        last_date = self.df.index.get_level_values('date')[-1].strftime("%d/%B/%Y")
        for field in self.get_fields():
            cfg = self._get_field_config(field)
            if field not in self.df.columns:
                continue
            value = locale.format_string(cfg['fmt'], self.df[field][-1], grouping=True).replace('nan', '-')
            if value != '-':
                last_data += f"  - {cfg['label']}: {value}\n"
        updated = "\n" + _("Information on last available data") + " (" + last_date + ")."
        note_Spain = ""
        if self.scope == 'spain':
            note_Spain = "\n" + _("Spain's data may take a few days to be consolidated and may be incomplete")
        return f"{last_data}\n__{updated}____{note_Spain}__"

    def _plot_data(self, plt, ax):
        x = self.df.index.get_level_values('date')
        _ = self.translation
        legend = []
        has_ax2 = False
        if self.get_category() == 'region':
            for field in self.get_fields():
                is_ax2 = False
                cfg = self._get_field_config(field)
                if not cfg['plot_type']:
                    continue
                if field not in self.df.columns:
                    legend.append(plt.plot(x, [0] * x.shape[0], color=cfg['color']))
                    continue
                if cfg['plot_type'] == 'fill_between':
                    legend.append(plt.fill_between(x, 0, self.df[field], alpha=cfg['alpha'], color=cfg['color'], label=cfg['label']))
                    plt.plot(x, self.df[field], color=cfg['color'])
                elif cfg['plot_type'] == 'line':
                    ax.set_ylabel(cfg['label'], color=cfg['color'], fontsize=15)
                    ax.tick_params(axis='y', labelcolor=cfg['color'])
                    legend.append(ax.plot(x, self.df[field], alpha=cfg['alpha'], color=cfg['color'], linewidth=cfg['linewidth'], label=cfg['label']))
                elif cfg['plot_type'] == 'line2':
                    is_ax2 = True
                    has_ax2 = True
                    ax2 = ax.twinx()
                    ax2.grid(False)
                    ax2.set_ylabel(cfg['label'], color=cfg['color'], fontsize=15)
                    ax2.tick_params(axis='y', labelcolor=cfg['color'])
                    legend.append(ax2.plot(x, self.df[field], alpha=cfg['alpha'], color=cfg['color'], linewidth=cfg['linewidth'], label=cfg['label']))
                else:
                    legend.append(plt.bar(x, self.df[field], alpha=cfg['alpha'], width=cfg['width'], color=cfg['color'], label=cfg['label']))
                if cfg['annotate']:
                    value = locale.format_string(cfg['fmt'], self.df[field][-1], grouping=True).replace('nan', '-')
                    if is_ax2:
                        ax2.annotate(f"{value}", xy=(x[-1], self.df[field][-1]),
                                     xytext=(0, 3), textcoords="offset points", ha='center')
                    else:
                        ax.annotate(f"{value}", xy=(x[-1], self.df[field][-1]),
                                    xytext=(0, 3), textcoords="offset points", ha='center')
            if has_ax2:
                legends = [lgn[0] for lgn in legend]
                labels = [lgn.get_label() for lgn in legends]
                ax2.legend(legends, labels, loc='upper left', fontsize=17)
            elif len(legend) > 6:
                ax.legend(loc='upper left', ncol=2, fontsize=15)
            else:
                ax.legend(loc='upper left', fontsize=17)

        elif self.get_category() == 'multiregion':
            CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a', '#f781bf', '#a65628', '#984ea3', '#999999', '#e41a1c', '#dede00']
            field = self.get_fields()[0]
            self.region.sort(key=lambda region: self.df[self.df.region == region][field][-1], reverse=True)
            for region, color in zip(self.region, CB_color_cycle):
                df_region = self.df[self.df.region == region]
                x = df_region.index.get_level_values('date')
                region_name = _(region)
                v = locale.format_string('%.2f', df_region[field][-1], grouping=True).replace('nan', '-')
                label = f"{region_name} ({v})"
                if 'logarithmic' in self.get_name():
                    plt.yscale('log')
                plt.plot(x, df_region[field], linewidth=2, color=color, label=label)

    def _get_field_config(self, field):
        _ = self.translation
        grey_cycle = ['#7d755b', '#8d8670', '#9e9884', '#aea998', '#bebaad', '#cecbc1', '#dfdcd6', '#efeeea']

        # defaults
        cfg = {}
        cfg['alpha'] = 0.5
        cfg['width'] = 1
        cfg['linewidth'] = 1
        cfg['color'] = None
        cfg['label'] = None
        cfg['annotate'] = True
        cfg['plot_type'] = 'bar'
        cfg['fmt'] = '%.0f'

        if field == 'cases':
            cfg['label'] = _('Cases')
        elif field == 'increase_cases':
            cfg['label'] = _('Daily increment')
            cfg['width'] = 0.9
            cfg['alpha'] = 0.3
        elif field == 'rolling_cases':
            cfg['label'] = _('Increment rolling avg (7 days)')
            cfg['color'] = 'red'
            cfg['plot_type'] = 'fill_between'
            cfg['annotate'] = False
            cfg['fmt'] = '%.1f'
        elif field == 'increase_hosp':
            cfg['label'] = _('Daily increment')
            cfg['width'] = 0.9
            cfg['alpha'] = 0.6
            cfg['color'] = 'darkgoldenrod'
        elif field == 'rolling_hosp':
            cfg['label'] = _('Increment rolling avg (7 days)')
            cfg['color'] = 'olive'
            cfg['plot_type'] = 'fill_between'
            cfg['annotate'] = False
            cfg['fmt'] = '%.1f'
        elif field == 'active_cases':
            cfg['label'] = _('Active cases')
            cfg['alpha'] = 0.3
        elif field == 'cases_per_100k':
            cfg['label'] = _('Cases')
            cfg['fmt'] = '%.1f'
        elif field == 'recovered':
            cfg['label'] = _('Recovered')
            cfg['plot_type'] = 'fill_between'
            cfg['alpha'] = 0.3
            cfg['color'] = 'g'
        elif field == 'deceased':
            cfg['label'] = _('Deceased')
            cfg['color'] = 'red'
            cfg['alpha'] = 0.3
            cfg['plot_type'] = 'fill_between'
        elif field == 'rolling_deceased':
            cfg['label'] = _('Deaths rolling avg (7 days)')
            cfg['color'] = 'red'
            cfg['width'] = 0.2
            cfg['plot_type'] = 'fill_between'
            cfg['annotate'] = False
            cfg['fmt'] = '%.1f'
        elif field == 'increase_deceased':
            cfg['label'] = _('Daily deaths')
            cfg['width'] = 0.9
            cfg['color'] = 'red'
        elif field == 'hospitalized':
            cfg['label'] = _('Currently hospitalized')
            cfg['color'] = 'y'
            cfg['alpha'] = 0.5
        elif field == 'hosp_per_100k':
            cfg['label'] = _('Hospitalizations')
            cfg['color'] = 'y'
            cfg['fmt'] = '%.1f'
        if field == 'Rt':
            cfg['label'] = _('Reproduction Rate')
            cfg['color'] = 'purple'
            cfg['plot_type'] = 'line2'
            cfg['linewidth'] = 3
            cfg['fmt'] = '%.2f'
            cfg['alpha'] = 1
        if field == 'acum14_cases_per_100k':
            cfg['label'] = _("CI14/100k")
            cfg['color'] = 'goldenrod'
            cfg['linewidth'] = 3
            cfg['plot_type'] = 'line'
            cfg['fmt'] = '%.2f'
            cfg['alpha'] = 1
        if 'acum14_cases_per_100k_' in field:
            cfg['label'] = _("CI14/100k") + " " + self.df[field].notnull()[::-1].idxmax()[0].strftime("%d/%m/%Y")
            cfg['color'] = grey_cycle[::-1][int(field.split('_')[-1])]
            cfg['linewidth'] = 3
            cfg['plot_type'] = 'line'
            cfg['fmt'] = '%.2f'
            cfg['alpha'] = 1
        return cfg

    def _get_plot_xlim(self):
        if self.scope in ['spain', 'italy']:
            return np.datetime64('2020-03-01')

        # if cases have reached at least 1000, show since it reached 100. Else, 5 cases
        max_cases = np.max(self.df['cases'])
        if max_cases > 1000:
            dates_gt_100 = self.df[self.df.cases > 100].index.get_level_values('date')
            return dates_gt_100[0]
        else:
            dates_gt_5 = self.df[self.df.cases > 5].index.get_level_values('date')
            if len(dates_gt_5) > 0:
                return dates_gt_5[0]
        return None

    def _add_footer(self, ax):
        _ = self.translation

        footer_font = FontProperties()
        footer_font.set_family('serif')
        footer_font.set_style('italic')

        ds_credits = ""
        if self.scope == 'spain':
            ds_name = 'Datadista'
            ds_url = "https://github.com/datadista/datasets/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif self.scope == 'world':
            ds_name = 'JHU CSSE'
            ds_url = "https://github.com/pomber/covid19"
            ds_credits = _("Data source from {ds_name} through Pomber's JSON API (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif self.scope == 'austria':
            ds_name = 'covid-data-austria'
            ds_url = "https://github.com/Daniel-Breuss/covid-data-austria"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif self.scope == 'italy':
            ds_name = 'Ministero della Salute (Italia)'
            ds_url = "https://github.com/pcm-dpc/COVID-19"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif self.scope == 'france':
            ds_name = 'OpenCOVID19-fr'
            ds_url = "https://opencovid19.fr/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif self.scope in ['balears', 'mallorca', 'menorca', 'eivissa']:
            ds_name = 'www.caib.cat'
            ds_url = 'https://arcg.is/1vnKr1'
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        else:
            ds_name = 'Proyecto COVID-19'
            ds_url = "https://covid19tracking.narrativa.com/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)

        ax.set_xlabel(
            _('Generated by COVID19gram (telegram bot)') + "\n" + ds_credits,
            position=(1., 0.),
            fontproperties=footer_font,
            horizontalalignment='right')
