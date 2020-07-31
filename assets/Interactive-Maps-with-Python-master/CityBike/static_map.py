import pandas as pd
import folium
import datetime

bike_data=pd.read_csv(r"New York CityBike/201909-citibike-tripdata.csv")
bike_data["Start Time"] = pd.to_datetime(bike_data["starttime"])
bike_data["Stop Time"] = pd.to_datetime(bike_data["stoptime"])
bike_data["hour"] = bike_data["Start Time"].map(lambda x: x.hour)

def get_trip_counts_by_hour(selected_hour):
    locations = bike_data.groupby("start station id").first()
    locations = locations.loc[:, ["start station latitude", "start station longitude", "start station name"]]
    subset = bike_data[bike_data["hour"]==selected_hour]
    departure_counts =  subset.groupby("start station id").count()
    departure_counts = departure_counts.iloc[:,[0]]
    departure_counts.columns= ["Departure Count"]
    arrival_counts =  subset.groupby("end station id").count().iloc[:,[0]]
    arrival_counts.columns= ["Arrival Count"]
    trip_counts = departure_counts.join(locations).join(arrival_counts)
    return trip_counts

def plot_station_counts(trip_counts):
    folium_map = folium.Map(location=[40.738, -73.98], zoom_start=12, tiles="CartoDB dark_matter", width='100%')
    for index, row in trip_counts.iterrows():
        net_departures = abs(row["Departure Count"]-row["Arrival Count"])
        popup_text = "<strong><font size=1>Location:</strong> {} <br> <strong>Total Departures:</strong> {} <br><strong>Total Arrivals:</strong> {}<br> <strong>Net Departures:</strong> {}</font>"
        popup_text = popup_text.format(row["start station name"], row["Arrival Count"], row["Departure Count"], net_departures)   
        radius = net_departures/30
        if row["Departure Count"] > row["Arrival Count"]:
            color="#E37222"
        else:
            color="#0A8A9F"
        folium.CircleMarker(location=(row["start station latitude"], row["start station longitude"]),radius=radius, color=color, 
                            popup=folium.Popup(popup_text, max_width=750, max_height=750),fill=True).add_to(folium_map)
    return folium_map

trip_counts = get_trip_counts_by_hour(18)
plot_station_counts(trip_counts)
folium_map = plot_station_counts(trip_counts)
folium_map.save("Static_Map.html")