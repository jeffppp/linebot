# -*- coding: utf-8 -*-

import requests
import pandas as pd

#input format
"""
    location = "25.071331, 121.519930"   #latitude,longitude
    inform = ['name','vicinity','rating','price_level','opening_hours'] #
    nex = integer                          #Set if needed; otherwise set 0
    radius = "1000"                        #in meter
    types = "restaurant" 
    keyword= ""
"""

def findplacenb(location, inform, nex, radius = '1000', types = 'restaurant', keyword = ''):
    url = []
    response = []
    data = []
    
    apikey = "AIzaSyCkpJmCnuq_oFO1xBUFfT6y39_C7qQ1U_M" #
    
    url.append("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + location + "&radius=" + radius + "&type=" + types + "&keyword=" + keyword + "&key=" + apikey + "&language=zh-TW" + "&region=zh-TW")
    response.append(requests.get(url[0]))
    data.append([[response[0].json()['results'][i].get(j) for j in inform] for i in range(len(response[0].json()['results']))])
    df = pd.DataFrame(data[0])
    df.columns = inform
    if nex > 0:
        for n in range(nex):
            url.append("https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken=" + response[-1].json()['next_page_token'] + "&key=" + apikey)
            response.append(requests.get(url[-1]))
            data.append([[response[-1].json()['results'][i].get(j) for j in inform] for i in range(len(response[-1].json()['results']))])
            ndf = pd.DataFrame(data[-1])
            df.append(ndf, ignore_index=True)
    return df


