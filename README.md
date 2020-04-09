# covid19gram

Telegram bot to generate Spain's disease evolution using datadista dataset

Requirements:
```
 pip install -r requirements.txt
 git clone https://github.com/datadista/datasets
 git clone https://github.com/pomber/covid19.git
```


Usage:


```python
from covid19plot import COVID19Plot
cplt = COVID19Plot()

# get a list of regions
cplt.get_regions()
# return sample ['Andalucía', 'Aragón', 'Asturias', 'Baleares', 'Canarias', 'Cantabria', 'Castilla-La Mancha', 'Castilla y León', 'Cataluña', 'Ceuta', 'C. Valenciana', 'Extremadura', 'Galicia', 'Madrid', 'Melilla', 'Murcia', 'Navarra', 'País Vasco', 'La Rioja', 'Total']

# plots for a given region
# types of plots availables: 'daily_cases', 'daily_deceased', 'active_recovered_deceased', 'active', 'deceased', 'recovered', 'cases_normalized'
cplt.generate_plot('daily_cases', 'Baleares')
# return sample: 'images//en_Baleares_daily_cases_1585995406.png'

# multiregion plots
# types of multiregion plots availables: 'cases_normalized', 'deceased_normalized',
cplt.generate_multiregion_plot('cases_normalized', ['La Rioja', 'Baleares', 'Total', 'Cantabria'], language='en')
```

