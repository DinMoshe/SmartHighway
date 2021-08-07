import logging
import azure.functions as func
from azure.cosmos import exceptions, CosmosClient, PartitionKey
from .consts import *
from .traffic_classes import *
from azure.storage.table import TableService
import json
import numpy as np
from .statistics import *


# Table Storage connection:
connection_string = "DefaultEndpointsProtocol=https;AccountName=storageaccounttraffafbc;AccountKey=+gMPGEjh1jZOX2G5THqKQJRO2LRN7khLUddPQuilaxkHpmJtOilCd36s/zNY/zDwlseUOIFhqa5snpW/t3r5tw==;EndpointSuffix=core.windows.net"
table_service = TableService(connection_string=connection_string)


# Cosmos DB connection
endpoint = 'https://traffic-storage-account.documents.azure.com:443/'
key = 'ZLTsOwTzi7K3U4f23RZwlDkUpaRMx2oOAl7E6ArfyOm2MVf8p3U9zCEilMIutV6Er6JykwDlDtq3veRWXHw3gw=='
client = CosmosClient(endpoint, key)

# set all the things needed to query the CosmosDB container

# Create a database
# <create_database_if_not_exists>
database_name = 'TrafficInfo'
database = client.create_database_if_not_exists(id=database_name)
# </create_database_if_not_exists>

# Create a container
# Using a good partition key improves the performance of database operations.
# <create_container_if_not_exists>
container_name = 'Density'
container = database.create_container_if_not_exists(
    id=container_name, 
    partition_key=PartitionKey(path="/laneId"),
    offer_throughput=400
)
# </create_container_if_not_exists>



def insert_cars_into_queue(queue, cars):
    for i in range(cars):
        global LAST_CAR
        global CURRENT_TIME
        LAST_CAR += 1
        car = Car(CURRENT_TIME, LAST_CAR)
        queue.append(car)
    return queue


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


# get the information from the CosmosDB container. The number of cars and the occupancy in the lane.
def extract_data_from_table(lane_id):
    query = f"""SELECT * FROM c WHERE c.laneId = "{lane_id}" """

    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    logging.info(f"items returned from query = {items}")

    lane_object = items[0]

    return int(lane_object["num_moving_cars"]), int(lane_object["num_cars"]) #, json.loads(lane_object["occupancy"])


# this method updates the queue of cars in the item associated with doc_id in CosmosDB
def upsert_queue_in_table(queue, doc_id, container):
    logging.info('\n1.6 Upserting an item\n')

    read_item = container.read_item(item=doc_id, partition_key=doc_id) # read_item is a dictionary made from
	# the json file whose id is doc_id

    read_item['occupancy'] = json.dumps(queue) # update the occupancy
    response = container.upsert_item(body=read_item) # write updates to CosmosDB

    logging.info('Upserted Item\'s Id is {0}'.format(response['id']))


# converts a list of dictionaries to a list of Car objects.
def dicts_to_cars(curr_occupancy):    
    return [Car(int(car_dict["arrival_time"]), int(car_dict["car_id"])) for car_dict in curr_occupancy]


# adds number of cars (flow - by allowed capacity) to the roads entering the intersection
def add_flow():
    global IS_LIMITED_CAPACITY
    for edge in road_edges_lst:
        if edge.entering_traffic_light():
            lane_id = edge.get_origin() + "_" + edge.get_destination()
            added_flow, num_cars = extract_data_from_table(lane_id=lane_id)

            # set the occupancy from the table
            # print(type(curr_occupancy))
            curr_occupancy = insert_cars_into_queue([], num_cars - added_flow)
            edge.set_occupancy(curr_occupancy)

            edge_flow = len(edge.get_occupancy())
            capacity = edge.get_capacity()
            if (IS_LIMITED_CAPACITY and edge_flow + added_flow <= capacity) or not IS_LIMITED_CAPACITY:
                edge.set_occupancy(insert_cars_into_queue(edge.get_occupancy(), added_flow))
            else:
                added_flow = capacity - edge_flow
                edge.set_occupancy(insert_cars_into_queue(edge.get_occupancy(), added_flow))

            # update the queue in the table
            # upsert_queue_in_table(queue=edge.occupancy_to_list_of_dicts(), doc_id=lane_id, container=container)


# redacts number of cars (flow - by current flow) from the roads exiting
# the intersection
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


# switches the lights according to the loss. It returns the id of the green traffic light.
def switch_lights(quantum):
    for edge in road_edges_lst:
        loss = calculate_edge_loss(edge)
        loss_dict[edge.get_traffic_light_id()] += loss
    if loss_dict["t1"] < loss_dict["t2"]:
        green_light_id = "t1"
        red_light_id = "t2"
        green_light("t1", quantum)
    else:
        green_light_id = "t2"
        red_light_id = "t1"
        green_light("t2", quantum)
    
    return green_light_id, red_light_id


# print the current stage being executed
def print_stage(stage):
    print(stage)
    print(CURRENT_TIME)
    for l in road_edges_lst:
        print(str(l) + ": occupancy:" + str(len(l.get_occupancy())) + ", loss: " + str(calculate_edge_loss(l)))
    print()


def get_curr_time_and_id():
    got_entity = table_service.get_entity(table_name='TimeCount', partition_key="counter", row_key="0")
    return got_entity['CurrTime'], got_entity['LastId']


def update_curr_time_and_id():
    got_entity = table_service.get_entity(table_name='TimeCount', partition_key="counter", row_key="0")
    # update curr time
    got_entity["CurrTime"] += 1
    got_entity["LastId"] = LAST_CAR + 1
    table_service.update_entity(table_name='TimeCount', entity=got_entity)


# return a dictionary mapping between the lane id to the number of cars in it
def get_occupancy_dicts():
    num_car_dict = dict()
    for edge in road_edges_lst:
        if edge.entering_traffic_light():
            lane_id = edge.get_origin() + "_" + edge.get_destination()
            num_car_dict[lane_id] = len(edge.get_occupancy())

    return num_car_dict


def main(documents: func.DocumentList, signalRMessages: func.Out[str]) -> None:
    # if documents:
    #     logging.info('Document id: %s', documents[0]['id'])
    #     logging.info(documents[0])
    #     return
    # else:
    #     logging.info('no documents')

    global CURRENT_TIME
    global LAST_CAR

    # start the decision process
    init_distribution_dict()
    init_loss_dict()
    
    curr_time, last_id = get_curr_time_and_id()
    CURRENT_TIME, LAST_CAR = curr_time, last_id
        
    add_flow()
    print_stage("add")
    redact_poisson_flow()
    print_stage("redact")
    
    green_light_id, red_light_id = switch_lights(QUANTUM)
    print_stage("switch")
    
    update_curr_time_and_id()
    
    # create plots of the occupancy and density
    num_car_dict = get_occupancy_dicts()
    create_plots(num_car_dict)
    send_images()
    
    signalr_values = {green_light_id: 1, red_light_id: 0}
    signalRMessages.set(json.dumps({
        'target': 'newMessage',
        'arguments': [ signalr_values ]
    }))
