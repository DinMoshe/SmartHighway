
import azure.functions as func
from azure.cosmos import exceptions, CosmosClient, PartitionKey
import logging

from numpy.lib.function_base import average
import os
import cv2
import dlib
import time
import threading
import math
import numpy as np
import json

carCascade = cv2.CascadeClassifier('myhaar.xml')

WIDTH = 1280
HEIGHT = 720


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



def estimateSpeed(location1, location2):
	d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
	# ppm = location2[2] / carWidht
	ppm = 8.8
	d_meters = d_pixels / ppm
	#print("d_pixels=" + str(d_pixels), "d_meters=" + str(d_meters))
	fps = 18
	speed = d_meters * fps * 3.6
	return speed
	

def trackMultipleObjects(video):
    # param video: was originally received by the line: video = cv2.VideoCapture('videoTest.mp4')
    # It is a video to be analyzed
	rectangleColor = (0, 255, 0)
	frameCounter = 0
	currentCarID = 0
	fps = 0
	
	carTracker = {}
	carNumbers = {}
	carLocation1 = {}
	carLocation2 = {}
	speed = [None] * 1000
	
	# Write output to video file
	out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (WIDTH,HEIGHT))


	while True:
		start_time = time.time()
		rc, image = video.read()
		if type(image) == type(None):
			break
		
		image = cv2.resize(image, (WIDTH, HEIGHT))
		resultImage = image.copy()
		
		frameCounter = frameCounter + 1
		
		carIDtoDelete = []

		for carID in carTracker.keys():
			trackingQuality = carTracker[carID].update(image)
			
			if trackingQuality < 7:
				carIDtoDelete.append(carID)
				
		for carID in carIDtoDelete:
			print ('Removing carID ' + str(carID) + ' from list of trackers.')
			print ('Removing carID ' + str(carID) + ' previous location.')
			print ('Removing carID ' + str(carID) + ' current location.')
			carTracker.pop(carID, None)
			carLocation1.pop(carID, None)
			carLocation2.pop(carID, None)
		
		if not (frameCounter % 10):
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))
			
			for (_x, _y, _w, _h) in cars:
				x = int(_x)
				y = int(_y)
				w = int(_w)
				h = int(_h)
			
				x_bar = x + 0.5 * w
				y_bar = y + 0.5 * h
				
				matchCarID = None
			
				for carID in carTracker.keys():
					trackedPosition = carTracker[carID].get_position()
					
					t_x = int(trackedPosition.left())
					t_y = int(trackedPosition.top())
					t_w = int(trackedPosition.width())
					t_h = int(trackedPosition.height())
					
					t_x_bar = t_x + 0.5 * t_w
					t_y_bar = t_y + 0.5 * t_h

					# check if the current car is in the following box
					if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
						matchCarID = carID
				
				if matchCarID is None:
					print ('Creating new tracker ' + str(currentCarID))
					
					tracker = dlib.correlation_tracker()
					tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
					
					carTracker[currentCarID] = tracker
					carLocation1[currentCarID] = [x, y, w, h]

					currentCarID = currentCarID + 1
		
		#cv2.line(resultImage,(0,480),(1280,480),(255,0,0),5)


		for carID in carTracker.keys():
			trackedPosition = carTracker[carID].get_position()
					
			t_x = int(trackedPosition.left())
			t_y = int(trackedPosition.top())
			t_w = int(trackedPosition.width())
			t_h = int(trackedPosition.height())
			
			cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)
			
			# speed estimation
			carLocation2[carID] = [t_x, t_y, t_w, t_h]
		
		end_time = time.time()
		
		if not (end_time == start_time):
			fps = 1.0/(end_time - start_time)
		
		#cv2.putText(resultImage, 'FPS: ' + str(int(fps)), (620, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)


		for i in carLocation1.keys():	
			if frameCounter % 1 == 0:
				[x1, y1, w1, h1] = carLocation1[i]
				[x2, y2, w2, h2] = carLocation2[i]
		
				# print 'previous location: ' + str(carLocation1[i]) + ', current location: ' + str(carLocation2[i])
				carLocation1[i] = [x2, y2, w2, h2]
		
				# print 'new previous location: ' + str(carLocation1[i])
				if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
					if (speed[i] == None or speed[i] == 0) and y1 >= 275 and y1 <= 285:
						speed[i] = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2])

					#if y1 > 275 and y1 < 285:
					if speed[i] != None and y1 >= 180:
						cv2.putText(resultImage, str(int(speed[i])) + " km/hr", (int(x1 + w1/2), int(y1-5)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
					
					#print ('CarID ' + str(i) + ': speed is ' + str("%.2f" % round(speed[i], 0)) + ' km/h.\n')

					#else:
					#	cv2.putText(resultImage, "Far Object", (int(x1 + w1/2), int(y1)),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

						#print ('CarID ' + str(i) + ' Location1: ' + str(carLocation1[i]) + ' Location2: ' + str(carLocation2[i]) + ' speed is ' + str("%.2f" % round(speed[i], 0)) + ' km/h.\n')
		# cv2.imshow('result', resultImage)
		# Write the frame into the file 'output.avi'
		#out.write(resultImage)


		if cv2.waitKey(33) == 27:
			break
	
	cv2.destroyAllWindows()
	speed = np.array([item for item in speed if item is not None])
	logging.info(f"speed = {speed}")
	return speed, carTracker


def write_to_file(file_output, video_bytes):
	# Checks and deletes the output file
	# You cant have a existing file or it will through an error
	if os.path.isfile(file_output):
		os.remove(file_output)

	# opens the file 'output.avi' which is accessable as 'out_file'
	with open(file_output, "wb") as out_file:  # open for [w]riting as [b]inary
		out_file.write(video_bytes)


# this method updates the num_cars in the item associated with doc_id using
def upsert_item(container, doc_id, num_moving_cars, num_cars):
	logging.info('\n1.6 Upserting an item\n')

	read_item = container.read_item(item=doc_id, partition_key=doc_id) # read_item is a dictionary made from
	# the json file whose id is doc_id

	# read_item['subtotal'] = read_item['subtotal'] + 1 # update the number of upserts
	read_item['num_moving_cars'] = num_moving_cars
	read_item['num_cars'] = num_cars # update the number of cars
	response = container.upsert_item(body=read_item) # write updates to CosmosDB

	logging.info('Upserted Item\'s Id is {0}'.format(response['id']))


def main(req: func.HttpRequest) -> func.HttpResponse:
	logging.info('Python HTTP trigger function processed a request.')
	logging.info(f"files = {req.files}")

	file_output_name = "video_to_process.mp4"

	lane_id = req.params.get('lane_id')
	logging.info(f"lane_id = {lane_id}")


	# lane_id = req_body.get('lane_id')
	
	# video_bytes = req.files.values()[0].stream.read()

	# write_to_file(file_output=file_output, video_bytes=video_bytes)

	for input_file in req.files.values(): # should be only one file
		filename = input_file.filename
		contents = input_file.stream.read()

		# if filename == file_output:
		write_to_file(file_output_name, contents)
		video = cv2.VideoCapture(file_output_name)
		speed, carTracker = trackMultipleObjects(video)
		average_speed = np.mean(speed)
		moving_cars = np.array([item for item in speed if item > 5])
		logging.info(f"average speed = {average_speed}")
		num_moving_cars = len(moving_cars)
		num_cars = len(speed)
		upsert_item(container=container, doc_id=lane_id, num_moving_cars=num_moving_cars, num_cars=num_cars) # update the DB
		return func.HttpResponse(body=json.dumps({'average_speed': average_speed, "num_moving_cars": num_moving_cars, "num_cars": num_cars}), status_code=200)


	# these lines probably don't do anything
	video_param = req.params.get('video')
	if not video_param:
		try:
			req_body = req.get_json()
		except ValueError:
			pass
		else:
			video_param = req_body.get('video')  # this is the line that actually extracts the data in our case
	
	if video_param:
		video = cv2.VideoCapture(os.path.join("..", file_output_name))
		average_speed = trackMultipleObjects(video)
		logging.info(f"average speed = {average_speed}")
		return func.HttpResponse(body={'average_speed': average_speed}, status_code=200)
	else:
		return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

