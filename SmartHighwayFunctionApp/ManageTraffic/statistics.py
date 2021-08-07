import matplotlib.pyplot as plt
from azure.cosmos import exceptions, CosmosClient, PartitionKey
from azure.storage.table import TableService
import numpy as np
import json
import requests
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from azure.core.exceptions import ResourceExistsError


# for sending images
website_token = '1740115349:AAG07QZupB1h6bsghlzsItPg9z29Rv8gArU'
chat_id = '1347275938'

# load the data collected so far
JSON_NAME = 'plot_json.json'
with open(JSON_NAME, 'r') as file_json:
    data_points = json.load(file_json)

# data_points = {'north_t1': [], 'south_t1': [], 'east_t2': [], 'west_t2': []}

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


# get the information from the CosmosDB container. The number of cars and the occupancy in the lane.
def extract_data_from_table():
    query = f"""SELECT * FROM c"""

    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    return items


# add the last data point about the number of cars for each lane
def add_data_points(num_car_dict):
    # items = extract_data_from_table()
    
    # for item in items:
    #     lane_id = item["laneId"]
    #     data_points[lane_id].append(item["num_cars"])

    for lane_id, num_cars in num_car_dict.items():
        data_points[lane_id].append(num_cars)
        if len(data_points[lane_id]) > 2000:
            data_points[lane_id] = data_points[lane_id][1000:]

    with open(JSON_NAME, 'w') as json_file:
        json.dump(data_points, json_file, sort_keys=True, indent=4)


# lane id is the id, lane_data is the data we want to plot
def plot_density(lane_id, lane_data):
    x = np.arange(len(lane_data))
    plt.title(f"Data about {lane_id}")
    plt.plot(x, lane_data)
    plt.savefig(f"{lane_id}_plot.png")
    plt.clf()


# create the plots for every lane
def create_plots(num_car_dict):
    add_data_points(num_car_dict)
    for lane_id, lane_data in data_points.items():
        plot_density(lane_id, lane_data)


# function to send an image to the web app
def send_image(img_names):
    try:
        print("Azure Blob Storage v" + __version__ + " - Python quickstart sample")
        # storage account connection string
        connection_string = "DefaultEndpointsProtocol=https;AccountName=storageaccounttraffafbc;AccountKey=+gMPGEjh1jZOX2G5THqKQJRO2LRN7khLUddPQuilaxkHpmJtOilCd36s/zNY/zDwlseUOIFhqa5snpW/t3r5tw==;EndpointSuffix=core.windows.net"

        # Create the BlobServiceClient object which will be used to create a container client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create a unique name for the container
        container_name = "plots"

        # try:
        #     # Create the container
        #     container_client = blob_service_client.create_container(container_name)
        # except ResourceExistsError:
        #     pass

        for img_name in img_names:
            # Create a blob client using the local file name as the name for the blob
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=img_name)

            print("\nUploading to Azure Storage as blob:\n\t" + img_name)

            # Upload the created file
            with open(img_name, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
    except Exception as ex:
        print('Exception:')
        print(ex)


def send_images():
    img_names = [f"{lane}_plot.png" for lane in data_points.keys()]
    send_image(img_names)


# if __name__ == "__main__":
#     create_plots()




