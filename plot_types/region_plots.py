import abc
import numpy as np
from .base import COVID19PlotType, COVID19PlotTypeManager


class COVID19RegionPlotType(COVID19PlotType):

    __metaclass__ = abc.ABCMeta


class C19PT_daily_cases(COVID19RegionPlotType):

    _name = 'daily_cases'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        return _('Cases increase at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Cases')

    def get_fields(self):
        return ['cases', 'increase_cases', 'rolling_cases']

    def _get_field_config(self, field):
        cfg = super(C19PT_daily_cases, self)._get_field_config(field)
        # Do not plot cases. information only in caption
        if field == 'cases':
            cfg['plot_type'] = None
        return cfg


class C19PT_cases(COVID19RegionPlotType):

    _name = 'cases'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        return _('Cumulative cases at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Cases')

    def get_fields(self):
        return ['cases']


class C19PT_daily_hospitalized(COVID19RegionPlotType):

    _name = 'daily_hospitalized'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        return _('Hospitalization evolution at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Hospitalizations')

    def get_fields(self):
        return ['increase_hosp', 'rolling_hosp']


class C19PT_hospitalized(COVID19RegionPlotType):

    _name = 'hospitalized'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        return _('Active hospitalizations at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Hospitalizations')

    def get_fields(self):
        return ['hospitalized']


class C19PT_active(COVID19RegionPlotType):

    _name = 'active'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        if self.scope == 'france' and self.region != "total-france":
            return _('Active hospitalizations at {region}').format(region=_(self.region))
        return _('Active cases at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        if self.scope == 'france' and self.region != "total-france":
            return _('Hospitalizations')
        return _('Cases')

    def get_fields(self):
        if self.scope == 'france' and self.region != "total-france":
            return ['hospitalized']
        return ['active_cases']


class C19PT_active_recovered_deceased(COVID19RegionPlotType):

    _name = 'active_recovered_deceased'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        title = _('Active cases, recovered and deceased at {region}').format(region=_(self.region))
        if 'hospitalized' in self.df.columns:
            if self.region != 'total-france' and self.scope == 'france':
                title = _('Curr. hospitalized, recovered & deceased at {region}').format(region=_(self.region))
            else:
                title = _('Active, hospitalized, recovered and deceased at {region}').format(region=_(self.region))
        return title

    def get_y_label(self):
        _ = self.translation
        return _('Cases')

    def _get_field_config(self, field):
        cfg = super(C19PT_active_recovered_deceased, self)._get_field_config(field)
        cfg['plot_type'] = 'fill_between'
        # Do not plot cases if not spain. Information only in caption
        if field == 'cases' and self.scope != 'spain':
            cfg['plot_type'] = None
        return cfg

    def get_fields(self):
        fields = ['cases']
        if self.scope != 'spain' and np.max(self.df['active_cases']) > 0:
            fields.append('active_cases')
        if 'hospitalized' in self.df.columns:
            fields.append('hospitalized')
        if 'intensivecare' in self.df.columns:
            fields.append('intensivecare')
        if self.scope != 'spain':
            fields.append('recovered')
        fields.append('deceased')
        return fields


class C19PT_deceased(COVID19RegionPlotType):

    _name = 'deceased'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        return _('Deaths evolution at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Deaths')

    def get_fields(self):
        return ['deceased']


class C19PT_recovered(COVID19RegionPlotType):

    _name = 'recovered'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        return _('Recovered cases at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Cases')

    def get_fields(self):
        return ['recovered']


class C19PT_daily_deceased(COVID19RegionPlotType):

    _name = 'daily_deceased'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        return _('Daily deaths evolution at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Deaths')

    def _get_field_config(self, field):
        cfg = super(C19PT_daily_deceased, self)._get_field_config(field)
        # Do not plot deceased or case_fatality_rate. information only in caption
        if field == 'deceased' or field == 'case_fatality_rate':
            cfg['plot_type'] = None
        return cfg

    def get_fields(self):
        fields = ['deceased', 'increase_deceased', 'rolling_deceased']
        if 'case_fatality_rate' in self.df.columns:
            fields.append('case_fatality_rate')

        return fields


class C19PT_cases_normalized(COVID19RegionPlotType):

    _name = 'cases_normalized'

    def get_title(self):
        _ = self.translation
        return _('Cases per 100k inhabitants at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Cases')

    def get_fields(self):
        return ['cases_per_100k']


class C19PT_hosp_normalized(COVID19RegionPlotType):

    _name = 'hosp_normalized'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        return _('Hospitalizations per 100k inhabitants at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('Hospitalizations')

    def get_fields(self):
        return ['hosp_per_100k']


class C19PT_reproduction_rate(COVID19RegionPlotType):

    _name = 'reproduction_rate'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        if self.scope == 'france' and self.region != "total-france":
            return _('Recovered cases at {region}').format(region=_(self.region))
        return _('Reproduction Rate at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        if self.scope == 'france' and self.region != "total-france":
            return _('Cases')
        return _("CI14/100k")

    def get_fields(self):
        if self.scope == 'france' and self.region != "total-france":
            return ['recovered']
        return ['Rt', 'acum14_cases_per_100k']


class C19PT_consolidation_acum14(COVID19RegionPlotType):

    _name = 'consolidation_acum14'
    _category = 'region'

    def get_title(self):
        _ = self.translation
        return _('CI14 per 100k consolidation at {region}').format(region=_(self.region))

    def get_y_label(self):
        _ = self.translation
        return _('CI14 per 100k')

    def get_fields(self):
        return ['acum14_cases_per_100k_7', 'acum14_cases_per_100k_6', 'acum14_cases_per_100k_5', 'acum14_cases_per_100k_4', 'acum14_cases_per_100k_3', 'acum14_cases_per_100k_2', 'acum14_cases_per_100k_1', 'acum14_cases_per_100k']


def register_region_plots():
    for subclass in COVID19RegionPlotType.__subclasses__():
        COVID19PlotTypeManager.register_plot_type(subclass)
