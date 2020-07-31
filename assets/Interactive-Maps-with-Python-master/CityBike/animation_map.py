import pandas as pd
import geopandas as gpd
import folium, datetime
from folium.plugins import TimestampedGeoJson, HeatMapWithTime

nyc = pd.read_csv("CityBike/201909-citibike-tripdata.csv")
nyc['starttime'] = nyc['starttime'].str[:-5]
nyc['stoptime'] = nyc['stoptime'].str[:-5]
nyc['starttime'] = pd.to_datetime(nyc['starttime'])
nyc['stoptime'] = pd.to_datetime(nyc['stoptime'])
nyc = nyc.set_index('starttime')
nyc['type'] = 'station'
start = nyc.pivot_table('tripduration', 
                     index = ['start station id', 'start station latitude', 'start station longitude', nyc.index.hour], 
                     columns = 'type', aggfunc='count').reset_index()
days = nyc.index.day.max()
start['station'] = start['station']/days
start.columns = ['station_id', 'lat', 'lon', 'hour', 'count']
start['fillColor'] = '#0e6f7e'
start.loc[start['count']<1, 'fillColor'] = '#e37222'

def create_geojson_features(df):
    features = []
    for _, row in df.iterrows():
        feature = { 'type': 'Feature', 'geometry': { 'type':'Point', 'coordinates':[row['lon'],row['lat']]},
            'properties': {'time': pd.to_datetime(row['hour'], unit='h').__str__(), 'style': {'color' : ' '}, 'icon': 'circle',
                'iconstyle':{  'color': row['fillColor'], 'fillColor': row['fillColor'], 'fillOpacity': 0.8, 'stroke': 'true',
                 'fill':'true', 'radius': row['count'] + 1 }}}
        features.append(feature)
    return features

start_geojson = create_geojson_features(start)
nyc_map = folium.Map(location = [40.744916, -73.989830], tiles = "CartoDB dark_matter", zoom_start = 12.5)

TimestampedGeoJson(start_geojson, period = 'PT1H', duration = 'PT1M', transition_time = 800, auto_play = True).add_to(nyc_map)
nyc_map.save('LiveMap.html')

nyc1= nyc.reset_index().set_index('stoptime')
end = nyc1.pivot_table('tripduration',  index = ['end station id', 'end station latitude', 'end station longitude', nyc1.index.hour],
                     columns = 'type', aggfunc='count').reset_index()
end['station'] = end['station']/days
end.columns = ['station_id', 'lat', 'lon', 'hour', 'count']
end['fillColor'] = '#e64c4e'
end.loc[end['count']<1, 'fillColor'] = '#586065'
end_geojson = create_geojson_features(end)

df_hour_list = []
hours = pd.Series(nyc.index.hour.unique().sort_values())

def create_list(hour):
    df_hour_list.append(nyc.loc[nyc.index.hour == hour, ['start station latitude', 'start station longitude']].
                        groupby(['start station latitude', 'start station longitude']).sum().reset_index().values.tolist())
hours.apply(create_list);
map_time = folium.Map(location=[40.744916, -73.989830], tiles="CartoDB Positron", zoom_start=11.5)

HeatMapWithTime(df_hour_list, auto_play=True, max_opacity=0.7, 
                gradient = {0.2: '#FBD973', 0.4: '#fa782f', 0.75: '#F16578', 1: '#782890'}).add_to(map_time)
map_time.save('HeatMap.html')