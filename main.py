import json
import requests
import folium
import os
from geopy import distance
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_coffeshop_list(place):
    coffees = []
    with open("coffee.json", "r", encoding='CP1251') as my_file:
        file_content = my_file.read()
    content = json.loads(file_content)
    u_coords = fetch_coordinates(apikey, place)
    for coffee_shop in content:
        cord = (coffee_shop["Latitude_WGS84"], coffee_shop["Longitude_WGS84"])
        shop = {'title': coffee_shop["Name"],
                'distance': distance.distance(u_coords[::-1], cord).km,
                'latitude': float(coffee_shop["Latitude_WGS84"]),
                'longitude': float(coffee_shop["Longitude_WGS84"])}
        coffees.append(shop)
    nearest = sorted(coffees, key=get_user_posts)[:5]
    m = folium.Map(location=(u_coords[::-1]))
    for marker in nearest:
        folium.Marker(
            location=[marker['latitude'], marker['longitude']],
            tooltip="Click me!",
            popup=marker['title'],
            icon=folium.Icon(colour="blue"),
        ).add_to(m)
    m.save("index.html")
    return coffees


def get_user_posts(coffees):
    return coffees['distance']


if __name__ == '__main__':
    load_dotenv()
    apikey = os.environ["APIKEY"]
    place = input("Где вы находитесь? ")
    get_coffeshop_list(place)
