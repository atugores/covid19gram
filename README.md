# covid19gram

Telegram bot to generate Spain's disease evolution using datadista dataset

Requirements:
```
 pip install -r requirements.txt
 git clone https://github.com/datadista/datasets
```


Usage:


```python
from covid19plot import COVID19Plot
cplt = COVID19Plot()
cplt.get_regions()
# return sample ['Andalucía', 'Aragón', 'Asturias', 'Baleares', 'Canarias', 'Cantabria', 'Castilla-La Mancha', 'Castilla y León', 'Cataluña', 'Ceuta', 'C. Valenciana', 'Extremadura', 'Galicia', 'Madrid', 'Melilla', 'Murcia', 'Navarra', 'País Vasco', 'La Rioja', 'Total']
cplt.generate_plot('daily_cases', 'Baleares')
# return sample: 'images//en_Baleares_daily_cases_1585995406.png'
# current available type of plots: 'daily_cases', 'daily_deceased', 'active_recovered_deceased', 'active', 'deceased', 'recovered'
```

