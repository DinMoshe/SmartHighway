import math


class Car:
    def __init__(self, arrival_time, id):
        self.arrival_time = arrival_time
        self.id = id

    def __str__(self):
        return self.id + " arrival time:" + self.arrival_time

    def get_car_weight(self, current_time):
        return current_time - self.arrival_time + 1

    def get_arrival_time(self):
        return self.arrival_time


class Road:
    def __init__(self, origin, destination, capacity):
        self.origin = origin
        self.destination = destination
        self.capacity = capacity
        self.occupancy = list()

    def __str__(self):
        return self.origin + " to " + self.destination

    def get_origin(self):
        return self.origin

    def get_destination(self):
        return self.destination

    def get_capacity(self):
        return self.capacity

    def set_occupancy(self, occupancy_queue):
        self.occupancy = occupancy_queue
        if len(self.occupancy) > self.capacity:
            print("CAPACITY ERROR!")

    def get_occupancy(self):
        return self.occupancy

    # returns true of edged is entering a traffic light node
    def entering_traffic_light(self):
        return self.get_destination()[0] == 't'

    # returns traffic light id of an edge
    def get_traffic_light_id(self):
        if self.entering_traffic_light():
            return self.get_destination()
        return self.get_origin()

    def remove_cars_from_road(self, num_cars):
        for i in range(num_cars):
            self.occupancy.pop(0)


# Use when we have multiple types of intersections
class Intersection:
    def __init__(self, road_lst):
        self.roads = road_lst

    def get_road_lst(self):
        return self.roads
