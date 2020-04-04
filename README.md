# covid19gram

Telegram bot to generate Spain's disease evolution using datadista dataset

Usage:

```python
from covid19plot import COVID19Plot
cplt = COVID19Plot()
cplt.get_regions()
# return sample ['Andalucía', 'Aragón', 'Asturias', 'Baleares', 'Canarias', 'Cantabria', 'Castilla-La Mancha', 'Castilla y León', 'Cataluña', 'Ceuta', 'C. Valenciana', 'Extremadura', 'Galicia', 'Madrid', 'Melilla', 'Murcia', 'Navarra', 'País Vasco', 'La Rioja', 'Total']
cplt.generate_daily_cases_img('Baleares')
# return sample: 'images//Baleares_cases_1585995406.png'
```

