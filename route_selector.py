from geopy import geocoders
from geo_groups import RegionsTopLineDict
from datetime import datetime
from shapely.geometry import Point, Polygon
from geopy.geocoders import Nominatim
import itertools
import random
import math
from geopy.geocoders import Nominatim
from geopy.distance import distance
import pandas as pd


class RouteSelector:
    # <--- start ----- BLOCK 1 ----- start --->
    # This block of codes defines a function find_journey_scope. Function takes two arguments (start, end).
    # Function will return list of lists. [[start, neighbour, end], [start, neighbour, neighbour, end]]
    # All possible routes from start to end are returned.


    def find_journey_scope(self, start, end, planner=[]):
        """
        :param start: string representing the starting point of journey
        :param end: string representing the end point of the journey
        :param planner: Optional string representing the areas traveller is interested in.
        :return: list of lists containing all possible routes between start and end.
        """
        d = RegionsTopLineDict()
        region_top_line = d.summary

        geolocator = Nominatim(user_agent='Killi')
        start_cords_a = Point((geolocator.geocode(start).longitude, geolocator.geocode(start).latitude))
        start_cords_b = Point((geolocator.geocode(end).longitude, geolocator.geocode(end).latitude))
        start_ = ''
        end_ = ''
        for item in region_top_line:
            coordinates = (region_top_line[item]['cor'])
            zone = Polygon(coordinates)
            if start_cords_a.within(zone):
                start_ = item

            if start_cords_b.within(zone):
                end_ = item

        possible_routes = []
        if planner:
            possible_routes = [[start_, end_] + planner]
            return start_, end_, possible_routes
        else:
            # N = degree of seperation between start and end point.
            # (N=0 indicates they are in the same region N=1 indicate they are direct neighbours)


            end_friends = region_top_line[end_]['neighbours']
            starts_friends = region_top_line[start_]['neighbours']

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
            # TODO Add an additional argument. Exclude. This will be a list of strings. For element in string. if element in path, delete.

            # This builds an alternate list if the list of paths is too long.
            possible_routes_short = []
            possible_routes = sorted(possible_routes, key=len)
            lengths = list(set([len(a) for a in possible_routes]))
            lengths = lengths[:2]
            for p in possible_routes:
                if len(p) <= lengths[-1]:
                    possible_routes_short.append(p)

            if len(possible_routes) > 6:
                return start_, end_, possible_routes_short
            else:
                return start_, end_, possible_routes

    # <--- end ----- BLOCK 1 ----- end --->

    # <--- start ----- BLOCK 2 ----- start --->
    # This block will take 4 imputs (start_loc = end_loc =, start_date =, end_date = )
    # sunny = [] List of all cities in the travel route with a 1 for weather in the dates specified.
    # snowy = []
    # no_go = []

    def trip_details(self, start_date, end_date, start_city, end_city, stops, paths):
        """
        :param start_date: str. start date of Trip.
        :param end_date: str. end date of Trip.
        :param start_city: str. Start Location.
        :param end_city: str. End Location.
        :param stops: int. Number of desired stops.
        :param paths: List of strings representing all possible paths in route.
        :return:
        [0] Length Trip in Months
        [1] Length Trip in Days.
        [2] List of Tuples representing stops on trip.
        """
        d = RegionsTopLineDict()
        region_top_line = d.summary
        city_good_bad = d.weather_good_bad
        geolocator = Nominatim(user_agent='killi')

        start_cords = (geolocator.geocode(start_city).latitude, geolocator.geocode(start_city).longitude)

        end_cords = (geolocator.geocode(end_city).latitude, geolocator.geocode(end_city).longitude)

        start_date_formatted = datetime.strptime(start_date, '%d/%m/%Y')
        start_month = start_date_formatted.month

        end_date_formatted = datetime.strptime(end_date, '%d/%m/%Y')
        end_month = end_date_formatted.month
        end_year = end_date_formatted.year

        delta = end_date_formatted - start_date_formatted

        lenght_trip_days = delta.days
        lenght_trip_months = (end_date_formatted.year - start_date_formatted.year) * 12 + (
                end_date_formatted.month - start_date_formatted.month)

        # This loop creates a list of the Months in Trip.
        # The loop correct for the first year graduation (i.e. Dec > Jan) but no more.
        months_in_trip = [start_month]
        start_point = start_month

        if lenght_trip_months < 1:
            pass
        else:
            counter = 0
            for n in range(lenght_trip_months):
                if (n + 1) + start_point > 12:
                    counter += 1
                    months_in_trip.append(counter)
                else:
                    months_in_trip.append(start_month + (n + 1))

        # This loop returns a list of dictionaries. [ { city : [sliced_temp][sliced_wet][sliced_snow]}, {}... ]
        # sliced_temp represents the temp rating for a city ONLY for the months of the trip.
        container = []
        for item in city_good_bad:
            city_key = list(item.keys())[0]
            temp_list = list(item.values())[0]['temp']
            sliced_temp = [temp_list[n - 1] for n in months_in_trip]

            wet_list = list(item.values())[0]['wet']
            sliced_wet = [wet_list[n - 1] for n in months_in_trip]

            snow_list = list(item.values())[0]['snow']
            snow_wet = [wet_list[n - 1] for n in months_in_trip]

            city_good_bad = {city_key: [sliced_temp, sliced_wet, snow_wet]}
            container.append(city_good_bad)

        # This loop creates a List of dictionaries. [{ month of trip : [city, city, city] }, {}...]
        # The city returned meets the criteria of good to visit climate wise.
        # Temp > average and not outside the regional upper and lower limits.
        # Prcp < median of Top Quartile and not outside the regional upper and lower limits.

        monthly_good_list = []
        for i in range(len(months_in_trip)):
            monthly_good_list.append({i: []})
        for item in container:
            city_key_two = list(item.keys())[0]
            summary_values = list(item.values())[0]
            for i in range(len(months_in_trip)):
                if summary_values[0][i] == 1 and summary_values[1][i] != -1:
                    monthly_good_list[i][i].append(city_key_two)

        # This block of code creates cities in the route.

        # paths_in_journey = self.find_journey_scope(start_city, end_city)[2] #TODO THIS IS THE SPOT
        paths_in_journey = paths
        monthly_good_list_unpacked_merged = []
        for item in monthly_good_list:
            cities = list(item.values())[0]
            try:
                cities.remove(start_city)
                cities.remove(end_city)
            except ValueError:
                pass
            if cities != start_city or cities != end_city:
                monthly_good_list_unpacked_merged += cities
        list(set(monthly_good_list_unpacked_merged))

        cities_in_route = []
        for path in paths_in_journey:
            path_container = []
            for region in path:
                region_container = []
                for city in region_top_line[region]['cities']:
                    if city[0] in monthly_good_list_unpacked_merged:
                        region_container.append(city[2])
                path_container.append(region_container)
            cities_in_route.append(path_container)

        # This block of code takes the cities in route and returns a list of combos as tuples.

        combos_per_path = []
        for path in cities_in_route:
            merged_list = list(set(sum(path, [])))
            num_uniques = math.comb(len(merged_list), stops)
            if num_uniques > 500:
                samples = []
                while len(samples) < 500:
                    random_integers = random.sample(merged_list, stops)
                    if random_integers in samples:
                        pass
                    else:
                        samples.append(tuple(
                            random_integers))  # if set(samples).isdisjoint(itertools.combinations(random_integers, 3)):  #     samples.append(random_integers)
                combos_per_path.append(samples)
            else:
                combinations = itertools.combinations(merged_list, stops)
                combination_tuples = [tuple(x) for x in combinations]
                combos_per_path.append(combination_tuples)
        tuples_to_visit = [item for sublist in combos_per_path for item in sublist]

        return lenght_trip_months, lenght_trip_days, tuples_to_visit
    # <--- end ----- BLOCK 2 ----- end --->
