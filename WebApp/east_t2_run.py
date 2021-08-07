#!/usr/bin/env python
# coding: utf-8

import requests
import os
import random

url = "http://localhost:7071/api/ProcessVideo"
# url = "https://smarthighwayfunctionapp.azurewebsites.net/api/ProcessVideo?"

dir_path = "./videos"

random_file = random.choice(os.listdir(dir_path))

with open(os.path.join(dir_path, random_file), 'rb') as video:
    payload = {'video': video}
    my_json = dict({"lane_id": "east_t2"})
    response = requests.post(url, params=my_json, files=payload)
    print(response)

