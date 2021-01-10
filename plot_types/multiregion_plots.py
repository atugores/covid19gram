import abc
from .base import COVID19PlotType, COVID19PlotTypeManager


class COVID19RegionPlotType(COVID19PlotType):

    __metaclass__ = abc.ABCMeta


class C19PT_m_cases(COVID19RegionPlotType):

    _name = 'm_cases'
    _category = 'multiregion'

    def get_title(self):
        _ = self.translation
        return _('Cases')

    def get_y_label(self):
        _ = self.translation
        return _('Cases')

    def get_fields(self):
        return ['cases']


class C19PT_hospitalized(COVID19RegionPlotType):

    _name = 'm_hospitalized'
    _category = 'multiregion'

    def get_title(self):
        _ = self.translation
        return _('Hospitalizations')

    def get_y_label(self):
        _ = self.translation
        return _('Hospitalizations')

    def get_fields(self):
        return ['hospitalized']


class C19PT_m_acum14_cases_normalized(COVID19RegionPlotType):

    _name = 'm_acum14_cases_normalized'
    _category = 'multiregion'

    def get_title(self):
        _ = self.translation
        return _('Cumulative incidence (14 days/100k inhabitants)')

    def get_y_label(self):
        _ = self.translation
        return _('Cumulative cases')

    def get_fields(self):
        return ['acum14_cases_per_100k']


class C19PT_m_acum14_hospitalized_normalized(COVID19RegionPlotType):

    _name = 'm_acum14_hospitalized_normalized'
    _category = 'multiregion'

    def get_title(self):
        _ = self.translation
        return _('Cumulative incidence of hospitalizations (14 days/100k inhabitants)')

    def get_y_label(self):
        _ = self.translation
        return _('Cumulative cases')

    def get_fields(self):
        return ['acum14_hosp_per_100k']


class C19PT_m_cases_logarithmic(COVID19RegionPlotType):

    _name = 'm_cases_logarithmic'
    _category = 'multiregion'

    def get_title(self):
        _ = self.translation
        return _('Cases, Logarithmic Scale')

    def get_y_label(self):
        _ = self.translation
        return _('Cases')

    def get_fields(self):
        return ['cases']


class C19PT_m_cases_normalized(COVID19RegionPlotType):

    _name = 'm_cases_normalized'
    _category = 'multiregion'

    def get_title(self):
        _ = self.translation
        return _('Cases per 100k inhabitants')

    def get_y_label(self):
        _ = self.translation
        return _('Cases')

    def get_fields(self):
        return ['cases_per_100k']


class C19PT_m_hospitalized_logarithmic(COVID19RegionPlotType):

    _name = 'm_hospitalized_logarithmic'
    _category = 'multiregion'

    def get_title(self):
        _ = self.translation
        return _('Hospitalizations, Logarithmic Scale')

    def get_y_label(self):
        _ = self.translation
        return _('Hospitalizations')

    def get_fields(self):
        return ['hospitalized']


class C19PT_m_hospitalized_normalized(COVID19RegionPlotType):

    _name = 'm_hospitalized_normalized'
    _category = 'multiregion'

    def get_title(self):
        _ = self.translation
        return _('Hospitalizations per 100k inhabitants')

    def get_y_label(self):
        _ = self.translation
        return _('Hospitalizations')

    def get_fields(self):
        return ['hosp_per_100k']


class C19PT_m_deceased_normalized(COVID19RegionPlotType):

    _name = 'm_deceased_normalized'
    _category = 'multiregion'

    def get_title(self):
        _ = self.translation
        return _('Deceased per 100k inhabitants')

    def get_y_label(self):
        _ = self.translation
        return _('Deaths')

    def get_fields(self):
        return ['deceased_per_100k']


def register_multiregion_plots():
    for subclass in COVID19RegionPlotType.__subclasses__():
        COVID19PlotTypeManager.register_plot_type(subclass)
