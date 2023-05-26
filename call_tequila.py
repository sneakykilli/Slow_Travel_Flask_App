from geo_groups import RegionsTopLineDict
from shapely.geometry import Point, Polygon
import itertools
import random
import math
from geopy.geocoders import Nominatim
import requests
import time
import pandas as pd
from datetime import datetime, timedelta

# ----- USER INPUT ---- #
# fly_from = 'Dublin'
# fly_to = 'Sydney'
# date_from = '01/05/2023'
# date_to = '30/06/2023'
# return_from = '30/06/2023'
# return_to = '05/07/2023'
# stops = 5
# budget = 900
# planner = []
# ----- USER INPUT ---- #

# <--- start ----- BLOCK 1 ----- start --->


class CallTequila:

    def tequila_nomad_call(self, fly_from, fly_to, date_from, date_to, return_from, return_to, stops, budget, planner=[]):

        #Initilize Data class.
        d = RegionsTopLineDict()
        region_top_line = d.summary
        #Initilize Geopy. Assist start & end to regions.
        geolocator = Nominatim(user_agent='Killi')

        start_cords_a = Point((geolocator.geocode(fly_from).longitude, geolocator.geocode(fly_from).latitude))
        start_cords_b = Point((geolocator.geocode(fly_to).longitude, geolocator.geocode(fly_to).latitude))
        start_ = ''
        end_ = ''
        for item in region_top_line:
            coordinates = (region_top_line[item]['cor'])
            zone = Polygon(coordinates)
            if start_cords_a.within(zone):
                start_ = item

            if start_cords_b.within(zone):
                end_ = item
        #Find possible routes if Planner has value
        possible_routes = []
        if planner:
            possible_routes = [[start_, end_] + planner] #TODO
        #Find possible routes if Planner has no value
        else:
            end_friends = region_top_line[end_]['neighbours']
            starts_friends = region_top_line[start_]['neighbours']
            # Degree of Seperation = N
            # N = 0 CHECK IF THEY ARE IN THE SAME REGION
            if start_ == end_:
                possible_routes.append(starts_friends)
            else:
                # N = 1 - CHECK IF START IN END'S NEIGHBOUR LIST.
                if start_ in end_friends:
                    possible_routes.append([start_, end_])
                # N = 2 - CHECK IF START AND END HAVE ANY COMMON NEIGHBOURS.
                for item in starts_friends:
                    if item in end_friends:
                        possible_routes.append([start_, item, end_])
                # N = 3 CHECK IF START'S NEIGHBOURS NEIGHBOURS ARE == END.
                starts_n2_friends = [{item: region_top_line[item]['neighbours']} for item in starts_friends]
                for item in starts_n2_friends:  # item is a dict. start_friend:[neighbours]
                    values = list(item.values())
                    key = list(item.keys())
                    starts_secondary_friends_list = values[0]
                    for region in starts_secondary_friends_list:
                        if region in end_friends:
                            possible_routes.append([start_, key[0], region, end_])
                # N = 4 CHECK IF START'S NEIGHBOURS NEIGHBOURS NEIGHBOURS == END.
                starts_n3_friends = []  # list containing [start's_friend : {start's_friend's_friend : [neighbours]}]
                for item in starts_n2_friends:
                    values = list(item.values())
                    key = list(item.keys())
                    for v in values[0]:
                        list_builder = {key[0]: {v: region_top_line[v]['neighbours']}}
                        starts_n3_friends.append(list_builder)

                for item in starts_n3_friends:
                    degree_one_f = list(item.keys())[0]
                    degree_two_f = list(list(item.values())[0].keys())[0]
                    degree_three_n = list(list(item.values())[0].values())[0]
                    for region in degree_three_n:
                        if region in end_friends:
                            possible_routes.append([start_, degree_one_f, degree_two_f, region, end_])
            #If Possible routes has too many options, select the shortest two.
            if len(possible_routes) > 6:
                # This builds an alternate list if the list of paths is too long.
                possible_routes_short = []
                possible_routes = sorted(possible_routes, key=len)
                lengths = list(set([len(a) for a in possible_routes]))
                lengths = lengths[:2]
                for p in possible_routes:
                    if len(p) <= lengths[-1]:
                        possible_routes_short.append(p)
                possible_routes = possible_routes_short
        # print(possible_routes)


        # <<< START BLOCK 2 >>>

        # Find the lat and long of start, end
        # ------------

        # Format dates to be used for calculating trip range.
        start_date_formatted = datetime.strptime(date_from, '%d/%m/%Y')
        start_month = start_date_formatted.month

        end_date_formatted = datetime.strptime(date_to, '%d/%m/%Y')
        end_month = end_date_formatted.month
        end_year = end_date_formatted.year

        delta = end_date_formatted - start_date_formatted

        lenght_trip_days = delta.days
        lenght_trip_months = (end_date_formatted.year - start_date_formatted.year) * 12 + (
                end_date_formatted.month - start_date_formatted.month)
        # ------------

        # This Block loops over every Path in possible_routes. For each path we replace region with cities.
        cities_in_route = []
        for path in possible_routes:
            container = []
            for stop in path:
                cities = region_top_line[stop]['cities']
                for city in cities:
                    code = city[2]
                    container.append(code)
            cities_in_route.append(container)
        # ------------
        #This block loops over cities in the route and creates unique combos depending on how many stops are choosen
        combos_per_path = []
        for path in cities_in_route:
            num_uniques = math.comb(len(path), stops)
            if num_uniques > 500:
                samples = []
                while len(samples) < 500:
                    random_integers = random.sample(path, stops)
                    if random_integers in samples:
                        pass
                    else:
                        samples.append(tuple(
                            random_integers))
                combos_per_path.append(samples)
            else:
                combinations = itertools.combinations(path, stops)
                combination_tuples = [tuple(x) for x in combinations]
                combos_per_path.append(combination_tuples)
        tuples_to_visit = [item for sublist in combos_per_path for item in sublist]
        # <<< END BLOCK 2 >>>

        #These are layovers. review for redundancy.
        test = tuples_to_visit
        trip_length_month = lenght_trip_months
        trip_length_days = lenght_trip_days
        max_nights = int(trip_length_days / stops)
        return_date_obj = datetime.strptime(date_to, '%d/%m/%Y')
        max_return_date = return_date_obj - timedelta(days=max_nights)
        return_date_str = datetime.strftime(max_return_date, '%d/%m/%Y')
        # ---------

        # ------ METHOD CALL 1 ------- #
        # Taking Start and End points and returning city codes for Nomad pull.

        headers = {'accept': 'application/json', 'apikey': '1ofvn-3b2Ahvp5vQ-BOqqkTJyggNFXe_', }

        params_1 = {'term': fly_from, 'locale': 'en-US', 'location_types': 'airport', 'limit': '1', 'active_only': 'true', }

        params_2 = {'term': fly_to, 'locale': 'en-US', 'location_types': 'airport', 'limit': '1', 'active_only': 'true', }

        response_1 = requests.get('https://api.tequila.kiwi.com/locations/query', params=params_1, headers=headers)
        response_2 = requests.get('https://api.tequila.kiwi.com/locations/query', params=params_2, headers=headers)

        start_city_code = response_1.json()['locations'][0]['id']
        end_city_code = response_2.json()['locations'][0]['id']
        # ----------

        # ------- METHOD 2 CALL ---------#
        url = 'https://api.tequila.kiwi.com/v2/nomad'
        API_KEY = '1ofvn-3b2Ahvp5vQ-BOqqkTJyggNFXe_'
        headers = {"Content-Type": "application/json; charset=utf-8", "apikey": API_KEY}

        requirements = {'adults': 1, 'date_from': date_from, 'date_to': return_to, 'return_from': return_from,
            'return_to': return_to, 'fly_from': start_city_code, 'fly_to': end_city_code, 'limit': 1, 'sort': 'quality',
            'max_stopovers': '1'}

        trips_container = []
        col = [f"{col}{i}" for i in range(1, stops + 2) for col in ["city", "country", "travel_time"]]
        columns = ['price', 'quality', 'link'] + col

        for element in test:
            time.sleep(0.33)
            holder = []
            for loc in element:
                locations = {'locations': [loc], 'nights_range': [3, max_nights]}
                holder.append(locations)
            data = {'via': holder}

            r = requests.post(url=url, json=data, params=requirements, headers=headers)
            data_dump = r.json()
            try:
                list_stops = (data_dump['data'][0]['route'])
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
                trips_container.append(trip_details)
                df = pd.DataFrame(trips_container, columns=columns)
                on_budget = df[df.price < budget].sort_values(by='price', ascending=True)
                by_price = df.sort_values(by='price', ascending=True)
                by_quality = df.sort_values(by='quality', ascending=True)

            except IndexError:
                pass
            except KeyError:
                pass

    # <--- end ----- BLOCK 2 ----- end --->

