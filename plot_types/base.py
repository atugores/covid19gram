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

    def __init__(self, scope, region, df, translation):
        self.scope = scope
        self.region = region
        self.translation = translation
        self.df = df

    @classmethod
    def get_name(cls):
        return cls._name

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
        has_cases = False
        for field in self.get_fields():
            cfg = self._get_field_config(field)
            if field not in self.df.columns:
                continue
            if 'cases' in field:
                has_cases = True
            value = locale.format_string(cfg['fmt'], self.df[field][-1], grouping=True).replace('nan', '-')
            last_data += f"  - {cfg['label']}: {value}\n"
        updated = "\n" + _("Information on last available data") + " (" + last_date + ")."
        note_Spain = ""
        if self.scope == 'spain' and has_cases:
            note_Spain = "\n" + _("From 19/04/2020, the accumulated cases are those detected by PCR test.")
        return f"{last_data}\n__{updated}____{note_Spain}__"

    def _plot_data(self, plt, ax):
        x = self.df.index.get_level_values('date')
        for field in self.get_fields():
            cfg = self._get_field_config(field)
            if not cfg['plot_type']:
                continue
            if field not in self.df.columns:
                plt.plot(x, [0] * x.shape[0], color=cfg['color'])
                continue
            if cfg['plot_type'] == 'fill_between':
                plt.fill_between(x, 0, self.df[field], alpha=cfg['alpha'], color=cfg['color'], label=cfg['label'])
                plt.plot(x, self.df[field], color=cfg['color'])
            else:
                plt.bar(x, self.df[field], alpha=cfg['alpha'], width=cfg['width'], color=cfg['color'], label=cfg['label'])
            if cfg['annotate']:
                ax.annotate(f"{self.df[field][-1]:0,.0f}", xy=(x[-1], self.df[field][-1]),
                            xytext=(0, 3), textcoords="offset points", ha='center')

    def _get_field_config(self, field):
        _ = self.translation

        # defaults
        cfg = {}
        cfg['alpha'] = 0.5
        cfg['width'] = 1
        cfg['color'] = None
        cfg['label'] = None
        cfg['annotate'] = True
        cfg['plot_type'] = 'bar'
        cfg['fmt'] = '%.0f'

        if field == 'cases':
            cfg['label'] = _('Cases')
        elif field == 'increase_cases':
            cfg['label'] = _('Daily increment')
        elif field == 'rolling_cases':
            cfg['label'] = _('Increment rolling avg (3 days)')
            cfg['color'] = 'red'
            cfg['plot_type'] = 'fill_between'
            cfg['annotate'] = False
            cfg['fmt'] = '%.1f'
        elif field == 'increase_hosp':
            cfg['label'] = _('Daily increment')
            cfg['color'] = 'darkgoldenrod'
        elif field == 'rolling_hosp':
            cfg['label'] = _('Increment rolling avg (3 days)')
            cfg['color'] = 'olive'
            cfg['plot_type'] = 'fill_between'
            cfg['annotate'] = False
            cfg['fmt'] = '%.1f'
        elif field == 'active_cases':
            cfg['label'] = _('Active cases')
        elif field == 'cases_per_100k':
            cfg['label'] = _('Cases')
            cfg['fmt'] = '%.1f'
        elif field == 'recovered':
            cfg['label'] = _('Recovered')
            cfg['color'] = 'g'
        elif field == 'deceased':
            cfg['label'] = _('Deceased')
            cfg['color'] = 'red'
        elif field == 'rolling_deceased':
            cfg['label'] = _('Deaths rolling avg (3 days)')
            cfg['color'] = 'red'
            cfg['plot_type'] = 'fill_between'
            cfg['annotate'] = False
            cfg['fmt'] = '%.1f'
        elif field == 'increase_deceased':
            cfg['label'] = _('Daily deaths')
            cfg['color'] = 'red'
        elif field == 'hospitalized':
            cfg['label'] = _('Currently hospitalized')
            cfg['color'] = 'y'
        elif field == 'hosp_per_100k':
            cfg['label'] = _('Hospitalizations')
            cfg['color'] = 'y'
            cfg['fmt'] = '%.1f'
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
        elif self.scope == 'italy':
            ds_name = 'Ministero della Salute (Italia)'
            ds_url = "https://github.com/pcm-dpc/COVID-19"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)
        elif self.scope == 'france':
            ds_name = 'OpenCOVID19-fr'
            ds_url = "https://opencovid19.fr/"
            ds_credits = _("Data source from {ds_name} (see {ds_url})").format(ds_name=ds_name, ds_url=ds_url)

        ax.set_xlabel(
            _('Generated by COVID19gram (telegram bot)') + "\n" + ds_credits,
            position=(1., 0.),
            fontproperties=footer_font,
            horizontalalignment='right')
