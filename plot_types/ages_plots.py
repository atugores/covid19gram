import abc
import locale
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from .base import COVID19PlotType, COVID19PlotTypeManager


class COVID19AgesPlotType(COVID19PlotType):

    __metaclass__ = abc.ABCMeta


class C19PT_ages(COVID19AgesPlotType):

    _name = 'ages'
    _category = 'ages'

    def get_title(self):
        _ = self.translation
        return _('Cases increase at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Cases')

    def get_fields(self):
        return ['cases', 'increase_cases', 'rolling_cases']

    def _get_field_config(self, field):
        cfg = super(C19PT_ages, self)._get_field_config(field)
        # Do not plot cases. information only in caption
        if field == 'cases':
            cfg['plot_type'] = None
        return cfg

    def _get_ages(self):
        last_date = self.df.index.get_level_values('date')[-1]
        today_df = self.df.loc[last_date]
        t = today_df['rango_edad'].unique().tolist()
        if 'Total' in t:
            t.remove('Total')
        t.sort()
        return t

    def _get_ages_df(self, sex=None, total=False):
        last_date = self.df.index.get_level_values('date')[-1]
        today_df = self.df.loc[last_date]
        if sex:
            today_df = today_df[today_df['sexo'] == sex]
        if not total:
            today_df = today_df[today_df['rango_edad'] != "Total"]
        return today_df

    def get_caption(self, image_path=None):
        _ = self.translation
        ages = self._get_ages()
        ages.append('Total')
        ambos_df = self._get_ages_df(sex='ambos', total=True)
        last_data = ""
        last_date = ambos_df.index.get_level_values('date')[-1].strftime("%d %B %Y")
        for age in ages:
            edad_df = ambos_df[ambos_df['rango_edad'] == age]
            E = edad_df['casos_confirmados'][-1]
            E_t = locale.format_string('%.0f', E, grouping=True)
            F = edad_df['fallecidos'][-1]
            F_t = locale.format_string('%.0f', F, grouping=True)
            L = 100 * F / E
            L_t = locale.format_string('%.2f', L)
            letal = _('case-fatality rate')
            tl_age = age.replace("y", _("y"))
            if age == 'Total':
                tl_age = _('Total')
            last_data = last_data + f"**    {tl_age}**: {E_t} ({F_t})  __{letal}:__ {L_t}%\n"
        last_data = last_data + "\n__" + _("*Data obtained from the analysis of reported cases with available information on age and sex.") + "__"
        updated = "\n" + _("Information on last available data") + " (" + last_date + ")."
        return f"{last_data}\n__{updated}__"

    def plot(self, image_path=None):
        _ = self.translation
        ages_df = self._get_ages_df()
        last_date = ages_df.index.get_level_values('date')[-1]
        title = _('Cases by age') + f" ({last_date:%d %B %Y})"
        edades = self._get_ages()

        women_deaths = list(ages_df[ages_df.sexo == 'mujeres']['fallecidos'])
        women_cases = list(ages_df[ages_df.sexo == 'mujeres']['casos_confirmados'])
        men_deaths = list(ages_df[ages_df.sexo == 'hombres']['fallecidos'])
        men_cases = list(ages_df[ages_df.sexo == 'hombres']['casos_confirmados'])

        max_value = max([max(women_cases), max(women_cases)])

        matplotlib.rc('axes', facecolor='white')
        matplotlib.rc('figure.subplot', wspace=.25)

        # Make figure background the same colors as axes
        fig = plt.figure(figsize=(12, 6), facecolor='white')

        # ---MEN data ---
        axes_left = plt.subplot(121)
        # Keep only top and right spines
        axes_left.spines['left'].set_color('none')
        axes_left.spines['right'].set_zorder(10)
        axes_left.spines['bottom'].set_color('none')
        axes_left.xaxis.set_ticks_position('top')
        axes_left.yaxis.set_ticks_position('right')
        axes_left.spines['top'].set_position(('data', len(edades)))
        axes_left.spines['top'].set_color('w')

        # Set axes limits
        num_ticks = 9
        interval_ticks = (((max_value // (num_ticks - 1)) // 500) + 1) * 500
        max_graph = (num_ticks * interval_ticks) + 50
        plt.xlim(max_graph, 0)
        plt.ylim(0, len(edades))

        # Set ticks label
        m_xticks = [tck * interval_ticks for tck in range(num_ticks)]
        # m_xticks = [0, 2500, 5000, 7500, 10000, 12500, 15000, 17500]
        m_xticks_t = [_('MEN') if xtck == 0 else locale.format_string('%.0f', xtck, grouping=True) for xtck in m_xticks]
        w_xticks = m_xticks
        m_xticks.reverse()
        w_xticks_t = [_('WOMEN') if xtck == _('MEN') else xtck for xtck in m_xticks_t]
        m_xticks_t.reverse()
        plt.xticks(m_xticks, m_xticks_t)
        axes_left.get_xticklabels()[-1].set_weight('bold')
        axes_left.get_xticklines()[-1].set_markeredgewidth(0)
        for label in axes_left.get_xticklabels():
            label.set_fontsize(10)
        plt.yticks([])

        # Plot data
        for i in range(len(men_deaths)):
            H, h = 0.8, 0.55
            # Death
            value = men_cases[i]
            p = patches.Rectangle(
                (0, i + (1 - H) / 2.0), value, H, fill=True, transform=axes_left.transData,
                lw=0, facecolor='blue', alpha=0.4)
            axes_left.add_patch(p)
            # New cases
            value = men_deaths[i]
            p = patches.Rectangle(
                (0, i + (1 - h) / 2.0), value, h, fill=True, transform=axes_left.transData,
                lw=0, facecolor='blue', alpha=0.9)
            axes_left.add_patch(p)

        # Add a grid
        axes_left.grid(True, linestyle='--', which='major', color='grey', alpha=.25)

        # --- WOMEN data ---
        axes_right = plt.subplot(122, sharey=axes_left)
        # Keep only top and left spines
        axes_right.spines['right'].set_color('none')
        axes_right.spines['left'].set_zorder(10)
        axes_right.spines['bottom'].set_color('none')
        axes_right.xaxis.set_ticks_position('top')
        axes_right.yaxis.set_ticks_position('left')
        axes_right.spines['top'].set_position(('data', len(edades)))
        axes_right.spines['top'].set_color('w')

        # Set axes limits
        plt.xlim(0, max_graph)
        plt.ylim(0, len(edades))

        # Set ticks labels
        w_xticks.reverse()
        # m_xticks_t.reverse()
        plt.xticks(w_xticks, w_xticks_t)
        axes_right.get_xticklabels()[0].set_weight('bold')
        for label in axes_right.get_xticklabels():
            label.set_fontsize(10)
        axes_right.get_xticklines()[1].set_markeredgewidth(0)
        plt.yticks([])

        # Plot data
        for i in range(len(women_deaths)):
            H, h = 0.8, 0.55
            # Death
            value = women_cases[i]
            p = patches.Rectangle(
                (0, i + (1 - H) / 2.0), value, H, fill=True, transform=axes_right.transData,
                lw=0, facecolor='red', alpha=0.4)
            axes_right.add_patch(p)
            # New cases
            value = women_deaths[i]
            p = patches.Rectangle(
                (0, i + (1 - h) / 2.0), value, h, fill=True, transform=axes_right.transData,
                lw=0, facecolor='red', alpha=0.9)
            axes_right.add_patch(p)

        # Add a grid
        axes_right.grid(True, linestyle='--', which='major', color='grey', alpha=.25)

        # Y axis labels
        # We want them to be exactly in the middle of the two y spines
        for i in range(len(edades)):
            x1, y1 = axes_left.transData.transform_point((0, i + .5))
            x2, y2 = axes_right.transData.transform_point((0, i + .5))
            x, y = fig.transFigure.inverted().transform_point(((x1 + x2) / 2, y1))
            tl_age = edades[i].replace("y", _("y"))
            plt.text(x, y, tl_age, transform=fig.transFigure, fontsize=15, weight='bold',
                     horizontalalignment='center', verticalalignment='center')

        # Legend
        arrowprops = dict(arrowstyle="-", color='black',
                          connectionstyle="angle,angleA=0,angleB=90,rad=0")

        x = men_cases[-1]
        axes_left.annotate(_('NEW CASES'), xy=(x + 7000, 8.5), xycoords='data',
                           horizontalalignment='right', fontsize=10,
                           xytext=(-40, +20), textcoords='offset points',
                           arrowprops=arrowprops)

        x = men_deaths[-1]
        axes_left.annotate(_('DEATHS'), xy=(.85 * x, 8.5), xycoords='data',
                           horizontalalignment='right', fontsize=10, xytext=(-50, -25), textcoords='offset points',
                           arrowprops=arrowprops)

        x = women_cases[-1]
        axes_right.annotate(_('NEW CASES'), xy=(x + 4000, 8.5), xycoords='data',
                            horizontalalignment='left', fontsize=10, xytext=(+40, +20), textcoords='offset points',
                            arrowprops=arrowprops)

        x = women_deaths[-1]
        axes_right.annotate(_('DEATHS'), xy=(.9 * x, 8.5), xycoords='data',
                            horizontalalignment='left', fontsize=10,
                            xytext=(+50, -25), textcoords='offset points',
                            arrowprops=arrowprops)

        fig.text(0.5, 0.955, title, horizontalalignment='center', color='black', weight='bold', fontsize='20')
        # Done
        self._add_footer(axes_right)
        plt.savefig(image_path)
        plt.close()


def register_ages_plots():
    for subclass in COVID19AgesPlotType.__subclasses__():
        COVID19PlotTypeManager.register_plot_type(subclass)
