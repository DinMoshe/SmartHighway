import logging

import azure.functions as func

import requests
import os
import random
from threading import Thread

lane_ids = ["east_t2", "west_t2", "north_t1", "south_t1"]
# url_process_video = "http://localhost:7071/api/ProcessVideo"
url_process_video = "https://smarthighwayfunctionapp.azurewebsites.net/api/ProcessVideo?"
dir_path = "./videos"


# this method receives a lane_id, chosses a random video and sends it to the process video function app.
def simulate_lane(lane_id):
    random_file = random.choice(os.listdir(dir_path))

    with open(os.path.join(dir_path, random_file), 'rb') as video:
        payload = {'video': video}
        my_json = dict({"lane_id": lane_id})
        response = requests.post(url_process_video, params=my_json, files=payload)
        print(response)


# this method receives number of times to simulate video capturing.
# It runs calls to the video processing function app.
def simulate(num_times):
    threads = []
    for i in range(num_times):
        for lane_id in lane_ids:
            # to use threading uncomment theses lines:
            # t = Thread(target=simulate_lane, args=(lane_id,))
            # threads.append(t)
            # t.start()

            # serial execution
            simulate_lane(lane_id)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    num_times = req.params.get('num_times')
    if not num_times:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            num_times = req_body.get('num_times')
    
    num_times = int(num_times)

    simulate(num_times=num_times)

    return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200,
            headers={'Access-Control-Allow-Origin': '*'}
    )
