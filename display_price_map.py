import plotly.plotly as py
import pandas as pd

df = pd.read_csv('collected_stats.dat')
df.head()

df['text'] = df['price_m2']

c_min = df['price_m2'].min()
c_max = df['price_m2'].max()

print c_min
print c_max

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

data = [ dict(
        type = 'scattergeo',
        locationmode = 'Europe',
        lon = df['lon'],
        lat = df['lat'],
        text = df['text'],
        mode = 'markers',
        marker = dict(
            size = 8,
            opacity = 0.8,
            reversescale = True,
            autocolorscale = False,
            symbol = 'square',
            line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale = scl,
            cmin = c_min,
            color = df['price_m2'],
            cmax = c_max,
            colorbar=dict(
                title="Price per square meter"
            )
        ))]


layout = dict(
        title = 'Price per square meter',
        colorbar = True,
        geo = dict(
            scope='europe',
            #projection=dict( type='albers usa' ),
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(217, 217, 217)",
            countrycolor = "rgb(217, 217, 217)",
            countrywidth = 0.5,
            subunitwidth = 0.5
        ),
    )

fig = dict( data=data, layout=layout )
py.iplot( fig, validate=False, filename='collected_stats.dat' )
