import matplotlib.pyplot as plt
import random
from consts import *
import numpy as np


def insert_cars_into_queue(queue, cars):
    for i in range(cars):
        global LAST_CAR
        global CURRENT_TIME
        LAST_CAR += 1
        car = Car(CURRENT_TIME, LAST_CAR)
        queue.append(car)
    return queue


def clean_roads():
    for edge in road_edges_lst:
        edge.set_occupancy([])


def transfer_cars_q1_to_q2(q1, q2, cars):
    for i in range(cars):
        if len(q1) == 0:
            break
        car = q1.pop(0)
        q2.append(car)
    return q1, q2


def init_distribution_dict():
    i = 0
    global lambda_lst
    for edge in road_edges_lst:
        if not edge.entering_traffic_light():
            distribution_dict[edge] = lambda_lst[i]
            e = get_succ_edge(edge)
            distribution_dict[e] = lambda_lst[i]
            i += 1


# initializes loss dict to zeroes
def init_loss_dict():
    loss_dict["t1"] = 0
    loss_dict["t2"] = 0


# returns a successor edge of edge
def get_succ_edge(edge):
    if edge.entering_traffic_light():
        return None
    for e in road_edges_lst:
        if e.entering_traffic_light() and e.get_destination() == edge.get_origin() \
                and e.get_origin() != edge.get_destination():
            return e
    return None


# adds random number of cars (flow - by allowed capacity) to the roads entering the intersection
def add_rand_flow():
    for edge in road_edges_lst:
        if edge.entering_traffic_light():
            capacity = edge.get_capacity()
            added_cars = random.randint(0, capacity - len(edge.get_occupancy()))
            q = insert_cars_into_queue(edge.get_occupancy(), added_cars)
            edge.set_occupancy(q)


# redacts random number of cars (flow - by current flow) from the roads exiting
# the intersection
def redact_rand_flow():
    for edge in road_edges_lst:
        if not edge.entering_traffic_light():
            cars_num = len(edge.get_occupancy())
            redacted_cars = random.randint(0, cars_num)
            edge.remove_cars_from_road(redacted_cars)


# adds number of cars (flow - by allowed capacity) to the roads entering the intersection by poisson distribution
def add_poisson_flow():
    global IS_LIMITED_CAPACITY
    for edge in road_edges_lst:
        if edge.entering_traffic_light():
            added_flow = np.random.poisson(distribution_dict[edge], 1)[0]
            edge_flow = len(edge.get_occupancy())
            capacity = edge.get_capacity()
            if (IS_LIMITED_CAPACITY and edge_flow + added_flow <= capacity) or not IS_LIMITED_CAPACITY:
                edge.set_occupancy(insert_cars_into_queue(edge.get_occupancy(), added_flow))
            else:
                added_flow = capacity - edge_flow
                edge.set_occupancy(insert_cars_into_queue(edge.get_occupancy(), added_flow))


# redacts number of cars (flow - by current flow) from the roads exiting
# the intersection by poisson distribution
def redact_poisson_flow():
    for edge in road_edges_lst:
        if not edge.entering_traffic_light():
            cars_num = len(edge.get_occupancy())
            redacted_cars = np.random.poisson(distribution_dict[edge], 1)[0]
            if redacted_cars > cars_num:
                redacted_cars = cars_num
            edge.remove_cars_from_road(redacted_cars)


# given to edges that theirs light has been turned green, updates the number of cars (flow)
# under the assumption all cars have crossed
def update_green_light_flow(succ_edge, edge, quantum):
    global IS_LIMITED_CAPACITY
    is_limited_capacity = IS_LIMITED_CAPACITY
    added_flow = min(quantum, len(succ_edge.get_occupancy()))
    capacity = edge.get_capacity()
    edge_flow = len(edge.get_occupancy())
    if not is_limited_capacity:
        succ_edge_q, edge_q = transfer_cars_q1_to_q2(succ_edge.get_occupancy(),
                                                     edge.get_occupancy(), added_flow)
        succ_edge.set_occupancy(succ_edge_q)
        edge.set_occupancy(edge_q)
        return

    if edge_flow + added_flow <= capacity:
        succ_edge_q, edge_q = transfer_cars_q1_to_q2(succ_edge.get_occupancy(),
                                                     edge.get_occupancy(), added_flow)
    else:
        real_flow = capacity - len(edge.get_occupancy())
        succ_edge_q, edge_q = transfer_cars_q1_to_q2(succ_edge.get_occupancy(),
                                                     edge.get_occupancy(), real_flow)
    succ_edge.set_occupancy(succ_edge_q)
    edge.set_occupancy(edge_q)


# given a light that has been switched to green, updates all relevant edge's flows
def green_light(light, quantum):
    for edge in road_edges_lst:
        if not edge.entering_traffic_light() and edge.get_origin() == light:
            succ_edge = get_succ_edge(edge)
            if succ_edge is not None:
                update_green_light_flow(succ_edge, edge, quantum)


def calculate_queue_weight(queue):
    loss = 0
    global CURRENT_TIME
    for car in queue:
        loss += car.get_car_weight(CURRENT_TIME)
    return loss


# calculate a loss to each edge
def calculate_edge_loss(edge):
    # this edge is not going into the intersection
    if not edge.entering_traffic_light():
        return 0
    loss = 0
    for e in road_edges_lst:
        if e.entering_traffic_light() and e.get_destination() != edge.get_destination():
            loss += calculate_queue_weight(e.get_occupancy())
    return loss


# switches the lights according to the loss
def switch_lights(quantum):
    for edge in road_edges_lst:
        loss = calculate_edge_loss(edge)
        loss_dict[edge.get_traffic_light_id()] += loss
    if loss_dict["t1"] < loss_dict["t2"]:
        green_light("t1", quantum)
    else:
        green_light("t2", quantum)


def get_avg_waiting_time(edge):
    global CURRENT_TIME
    queue = edge.get_occupancy()
    total_waiting_time = 0
    if len(queue) == 0:
        return 0
    for car in queue:
        total_waiting_time += (CURRENT_TIME - car.get_arrival_time())
    avg = float(total_waiting_time) / float(len(queue))
    return avg


def get_max_waiting_time(edge):
    global CURRENT_TIME
    queue = edge.get_occupancy()
    if len(queue) == 0:
        return 0
    return CURRENT_TIME - queue[0].get_arrival_time()


def plot_all(edge, avg_time_quantum, min_q, max_q, stat_type, time_limit, is_poisson=False):
    my_time = [i for i in range(time_limit)]
    for q in range(min_q, max_q):
        y_axis = avg_time_quantum[q]
        plt.legend()
        if is_poisson:
            titl = str(distribution_dict[edge])
            plt.title("lambda = " + titl)
        plt.plot(my_time, y_axis, label=str("line " + str(q)))
    plt.savefig(str(edge.get_origin()) + ' to ' + str(edge.get_destination()) + '_' + stat_type + '.png')
    plt.clf()
    # plt.show()


def stat_avg_quantum():
    global CURRENT_TIME
    global IS_POISSON
    is_poisson = IS_POISSON
    max_q = 20
    min_q = 10
    time_limit = 100
    n = 100
    for e in road_edges_lst:
        avg_time_quantum = np.zeros((max_q, time_limit))
        for q in range(min_q, max_q):
            for i in range(n):
                CURRENT_TIME = 0
                init_distribution_dict()
                init_loss_dict()
                clean_roads()
                for time in range(time_limit):
                    CURRENT_TIME += 1
                    if IS_POISSON:
                        add_poisson_flow()
                        redact_poisson_flow()
                    else:
                        add_rand_flow()
                        redact_rand_flow()
                    switch_lights(q)
                    avg_time_quantum[q][time] += get_avg_waiting_time(e)

        avg_time_quantum = avg_time_quantum / n
        plot_all(e, avg_time_quantum, min_q, max_q, "avg", time_limit, is_poisson)


def stat_max_quantum():
    global CURRENT_TIME
    global IS_POISSON
    is_poisson = IS_POISSON
    max_q = 20
    min_q = 10
    time_limit = 100
    n = 100
    for e in road_edges_lst:
        avg_time_quantum = np.zeros((max_q, time_limit))
        for q in range(min_q, max_q):
            for i in range(n):
                CURRENT_TIME = 0
                init_distribution_dict()
                init_loss_dict()
                clean_roads()
                for time in range(time_limit):
                    CURRENT_TIME += 1
                    if IS_POISSON:
                        add_poisson_flow()
                        redact_poisson_flow()
                    else:
                        add_rand_flow()
                        redact_rand_flow()
                    switch_lights(q)
                    avg_time_quantum[q][time] += get_max_waiting_time(e)

        avg_time_quantum = avg_time_quantum / 100
        plot_all(e, avg_time_quantum, min_q, max_q, "avg", time_limit, is_poisson)


def print_stage(stage):
    print(stage)
    print(CURRENT_TIME)
    for l in road_edges_lst:
        print(str(l) + ": occupancy:" + str(len(l.get_occupancy())) + ", loss: " + str(calculate_edge_loss(l)))
    print()


if __name__ == "__main__":
    # stat_avg_quantum()
    # stat_max_quantum()

    init_distribution_dict()
    init_loss_dict()
    for i in range(100):
        CURRENT_TIME += 1
        if IS_POISSON:
            add_poisson_flow()
            print_stage("add")
            redact_poisson_flow()
            print_stage("redact")
        else:
            add_rand_flow()
            print_stage("add")
            redact_rand_flow()
            print_stage("redact")

        switch_lights(QUANTUM)
        print_stage("switch")
