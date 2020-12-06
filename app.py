#!/usr/bin/env python3

##
# @file app.py
#
# @brief Flask web application for streaming video
#           from Raspberrry Pi camera V1
#
# @details 
#         Author: Isaac Marquez
#         Obstacle Avoidance on RPI4
#         OpenCV 4.4.0
#         November, 2020

# //////////////////////////////////////////////////
# Import the necessary packages
# //////////////////////////////////////////////////

from ImageProcessing.MotionDetector import MotionDetector
from picamera.array import PiRGBArray
from picamera import PiCamera
from flask import Flask, Response, render_template
import numpy as np
import imutils
import cv2
import threading
import time

# //////////////////////////////////////////////////
# Global constants and Objects
# //////////////////////////////////////////////////

# global lock for the current out frame
frame_lock = threading.Lock()

# gobal variable used to store the current output frame for the website
out_frame = None

# global variable for the flask application
app = Flask(__name__)

# global variables to store the host ip and port number
HOST_IP   = '192.168.1.9'
HOST_PORT = '5000'

# global constant to hold the minimum number of frames
# to construct a backgournd image
BACKGROUND_FRAME_COUNT_DEFAULT = 50

# the resolution of the camera and frame rate
CAMERA_WIDTH  =            640
CAMERA_HEIGHT =            480
CAMERA_FRAME_RATE =         30 

# color used for bounding box
BOX_COLOR = (255,0,0)

# //////////////////////////////////////////////////
# Initialize the Camera 
# //////////////////////////////////////////////////

# Initialize the pi camera object
pi_camera = PiCamera()
 
# Set the camera resolution -- the smaller the faster
# the processing => i use a 640 x 480 window
pi_camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
 
# Set the framerate of the camera
pi_camera.framerate = CAMERA_FRAME_RATE

# Create a link with the camera to get the raw data 
raw_capture = PiRGBArray(pi_camera, size=(CAMERA_WIDTH, CAMERA_HEIGHT))

# Wait a 0.1 seconds to allow the camera time to warmup
time.sleep(0.1)
 
# //////////////////////////////////////////////////
# Public Methods
# //////////////////////////////////////////////////

# Method to Draw a bounding box on the passed in frame
def DrawBoundingBox(frame, areas, contours):
	# find the largest moving object in the image
	max_index = np.argmax(areas)

	# Draw the bounding box
	countour = contours[max_index]
	(x, y, w, h) = cv2.boundingRect(countour)
	cv2.rectangle(frame, (x, y), (x+w, x+h), BOX_COLOR, 3)

	# Draw a circle at the center of teh bounding box
	circle_x = x + int(w/2)
	circle_y = y + int(h/2)
	cv2.circle(frame, (circle_x, circle_y), 4, BOX_COLOR, 1)

	# Draw the coordinates of the center of teh bounding box
	coords = "x: " + str(circle_x) + ", y: " + str(circle_y)
	cv2.putText(frame, coords, (circle_x - 10, circle_y - 10),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, BOX_COLOR, 2)

# Method for detecting motion within the out_frame
def DetectMotion():

	# store the current values stored of the global variables
	# out_frame, pi_camera, and the frame_lock
	global out_frame, pi_camera, frame_lock

	# initialize the motion detector object
	motion_detector = MotionDetector()

	# Capture frames continuously from the camera
	for frame in pi_camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
		# grab the raw array data from the current frame
		current_frame = frame.array

		# detect motion using the MotionDetector object
		(contours, areas) = motion_detector.DetectMotion(current_frame)

		# if contours were found, draw a bounding box on the 
		# image around the largest moving object
		if len(areas) > 0:
			DrawBoundingBox(current_frame, areas, contours)

		# store the current frame as the output frame
		with frame_lock:
			out_frame = current_frame.copy()

		# Clear the stream in preparation for the next frame
		raw_capture.truncate(0)

# Method for generating a frame for output to the flask app
def GrabFrame():

	# store the lock and out_frame values
	global out_frame, frame_lock

	# indefinitely loop over the frames
	while True:
		# wait until the lock is free for the out_frame
		with frame_lock:
			# keep looping if there is not an availiable out_frames
			if out_frame is None:
				continue

			# convert the image to JPEG
			(result, jpg_image) = cv2.imencode(".jpg", out_frame)

		# out the JPEG image to the application
		yield(b'--frame\r\n' 
			b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(jpg_image) + b'\r\n')

# //////////////////////////////////////////////////
# Public Routes
# //////////////////////////////////////////////////

# route the home page to render index.html
@app.route("/")
def Index():
	return render_template("index.html")

# route the video stream to GenerateFrame() function
@app.route("/VideoFeed")
def VideoFeed():
	return Response(GrabFrame(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# //////////////////////////////////////////////////
# Main Method
# //////////////////////////////////////////////////

# -- Main Method to start the flask app -- 
if __name__ == '__main__':

	# create a single daemon thread for detecting motion
	motion_thread = threading.Thread(target=DetectMotion)
	motion_thread.daemon = True
	motion_thread.start()

	# start the flask app
	app.run(host=HOST_IP, port=HOST_PORT, debug=True,
		threaded=True, use_reloader=False)
