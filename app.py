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
from imutils.video import VideoStream
from flask import Flask, Response, render_template
import imutils
import cv2
import threading
import time

# //////////////////////////////////////////////////
# Global constants
# //////////////////////////////////////////////////

# global lock for the current out frame
frame_lock = threading.Lock()

# gobal variable used to store the current output frame for the website
out_frame = None

# global variable for the flask application
app = Flask(__name__)

# global variable for the video stream
video_stream = VideoStream(usePiCamera=1).start()
time.sleep(2.0) # warm-up the camera

# global variables to store the host ip and port number
HOST_IP   = '192.168.1.17'
HOST_PORT = '5000'

# global constant to hold the minimum number of frames
# to construct a backgournd image
BACKGROUND_FRAME_COUNT_DEFAULT = 50

# //////////////////////////////////////////////////
# Public Methods
# //////////////////////////////////////////////////

# Method for detecting motion within the out_frame
def DetectMotion():

	# store the current values stored of the global variables
	# out_frame, video_stream, and the frame_lock
	global out_frame, video_stream, frame_lock

	# intialize the variable storing the number of frames processed to 0
	total_frames = 0

	# initialize the motion detector object
	motion_detector = MotionDetector()

	# indefinitely loop over the frames
	while True:
		# read in the next frame from the video and resize it
		current_frame = video_stream.read()
		current_frame = imutils.resize(current_frame, width=400)

		# if the total number of frames is over the configurable 
		# threshold => then start detecting motion
		if total_frames > BACKGROUND_FRAME_COUNT_DEFAULT:
			# pass the current frame into the motion detector object
			bounding_box = motion_detector.DetectMotion(current_frame)

			# if there was motion => draw the bounding box onto the image
			if bounding_box is not None:
				(startX, startY, endX, endY) = bounding_box
				cv2.rectangle(current_frame, (startX, startY), (endX, endY), (255, 255, 0), 2)
		
		# increment the total numbers of frames recieved
		# also update the background model with the current frame
		motion_detector.UpdateBG(current_frame)
		total_frames += 1

		# store the current frame as the output frame
		with frame_lock:
			out_frame = current_frame.copy()

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

# release the video stream pointer
video_stream.stop()