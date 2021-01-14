import datetime
import json

import folium
import pycountry
import requests

import pandas as pd


def main():
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    start_date = yesterday.strftime("%Y-%m-%d")
    end_date = start_date

    endpoint = f'https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{start_date}/{end_date}'
    r = requests.get(endpoint)

    content = json.loads(r.content.decode())
    countries_data = []
    
    for countries in content["data"][start_date]:
        country = content["data"][start_date][countries]
        if type(country['deaths']) == int :
            countries_data.append(content["data"][start_date][countries])

    df = pd.DataFrame(countries_data)

    countries_with_most_deaths = sorted(countries_data, key=lambda country: country['deaths'], reverse=True)
    deaths_per_country = {}

    for i in range(0, 5):
        country = pycountry.countries.get(alpha_3=countries_with_most_deaths[i]["country_code"])
        deaths_per_country[country.name] = countries_with_most_deaths[i]["deaths"]

    print('Deaths per Country:\n')

    for country in deaths_per_country:
        print(country + ': ' + str(deaths_per_country[country]))

    m = folium.Map(location=[0, 0], zoom_start=2.5)

    with open('countries.geojson') as file:
        geojson = json.loads(file.read())

    folium.Choropleth(
        geo_data=geojson,
        name='choropleth',
        data=df,
        columns=['country_code', 'deaths'],
        key_on='feature.properties.ISO_A3',
        bins=[0, 5000, 10000, 20000, 50000, 100000, 300000, countries_with_most_deaths[0]['deaths'] + 1],
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Deaths'
    ).add_to(m)

    folium.LayerControl().add_to(m)

    m.save("map.html")


if __name__ == "__main__":
    main()