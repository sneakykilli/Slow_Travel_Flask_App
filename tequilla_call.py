from app import app, db
from shots import Shots
from app import Trips, User, Results
import requests
import json
import gzip
from datetime import datetime, datetime, timedelta
import time
from route_selector import RouteSelector
import pandas as pd

with app.app_context():
    shots = Shots()
    today = datetime.today().date()
    trips = Trips.query.all()
    upcoming_trips = []
    for trip in trips:
        date_from = datetime.strptime(trip.date_from, '%d/%m/%Y').date()
        if date_from >= today:
            upcoming_trips.append(trip)
    for trip in upcoming_trips:
        planner_raw = trip.planner
        planner_list = [item.strip() for item in planner_raw.split(",")]
        trip_details = shots.trip_dets(fly_from=trip.fly_from, fly_to=trip.fly_to, date_from=trip.date_from, date_to=trip.date_to,
                                       stops=trip.stops, planner=planner_list)
        tuples_to_visit = trip_details[0]
        start_city_code = trip_details[1]
        end_city_code = trip_details[2]
        max_nights = trip_details[3]
        return_date_object = trip_details[4]
        max_return_date = trip_details[5]

        date_from = trip.date_from
        date_to = trip.date_to

        url = 'https://api.tequila.kiwi.com/v2/nomad'
        API_KEY = '1ofvn-3b2Ahvp5vQ-BOqqkTJyggNFXe_'
        headers = {"Content-Type": "application/json; charset=utf-8", "apikey": API_KEY}

        requirements = {'adults': 1, 'date_from': date_from, 'date_to': date_to, 'return_from': date_to,
                        'return_to': date_to, 'fly_from': start_city_code, 'fly_to': end_city_code, 'limit': 1,
                        'sort': 'quality', 'max_stopovers': '1'}

        col = [f"{col}{i}" for i in range(1, trip.stops + 2) for col in ["city", "country", "travel_time"]]
        columns = ['price', 'quality', 'link'] + col
        results_schema = ["id", "trip_id", "price", "quality",
                          "link", "city_1", "country_1", "travel_time_1",
                          "city_2", "country_2", "travel_time_2", "city_3",
                          "country_3", "travel_time_3", "city_4", "country_4",
                          "travel_time_4", "city_5", "country_5", "travel_time_5",
                          "city_6", "country_6", "travel_time_6", "city_7", "country_7",
                          "travel_time_7", "city_8", "country_8", "travel_time_8",
                          "city_9", "country_9", "travel_time_9", "city_10", "country_10","travel_time_10"]


        for element in tuples_to_visit:
            time.sleep(0.33)
            holder = []
            for loc in element:
                locations = {'locations': [loc], 'nights_range': [3, max_nights]}
                holder.append(locations)
            data = {'via': holder}

            trips_container = [None] * 34
            trips_container[0] = trip.id
            r = requests.post(url=url, json=data, params=requirements, headers=headers)
            data_dump = r.json()
            try:
                list_stops = data_dump['data'][0]['route']
                trip_details = []
                price = data_dump['data'][0]['price']
                trip_details.append(price)
                quality = data_dump['data'][0]['quality']
                trip_details.append(quality)
                link = data_dump['data'][0]['deep_link']
                trip_details.append(link)
                for stop in list_stops:
                    city_to = stop['cityTo']
                    country_to = stop['countryTo']['name']
                    utc_arv_time = stop['utc_arrival'][:-1]
                    utc_dept_time = stop['utc_departure'][:-1]
                    time_delta = datetime.fromisoformat(utc_arv_time) - datetime.fromisoformat(utc_dept_time)
                    travel_time = time_delta.total_seconds() / 3600
                    trip_details.append(city_to)
                    trip_details.append(country_to)
                    trip_details.append(travel_time)
                for index, item in enumerate(trip_details, start=1):
                    trips_container[index] = item
                new_result = Results(trip_id=trips_container[0], price=trips_container[1], quality=trips_container[2],
                    link=trips_container[3], city_1=trips_container[4], country_1=trips_container[5],
                    travel_time_1=trips_container[6], city_2=trips_container[7], country_2=trips_container[8],
                    travel_time_2=trips_container[9], city_3=trips_container[10], country_3=trips_container[11],
                    travel_time_3=trips_container[12], city_4=trips_container[13], country_4=trips_container[14],
                    travel_time_4=trips_container[15], city_5=trips_container[16], country_5=trips_container[17],
                    travel_time_5=trips_container[18], city_6=trips_container[19], country_6=trips_container[20],
                    travel_time_6=trips_container[21], city_7=trips_container[22], country_7=trips_container[23],
                    travel_time_7=trips_container[24], city_8=trips_container[25], country_8=trips_container[26],
                    travel_time_8=trips_container[27], city_9=trips_container[28], country_9=trips_container[29],
                    travel_time_9=trips_container[30], city_10=trips_container[31],country_10=trips_container[32],
                    travel_time_10=trips_container[33]
                )
                print(trips_container)
                db.session.add(new_result)
                db.session.commit()
            except IndexError:
                pass
            except KeyError:
                pass



