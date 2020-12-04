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
		# read in the next frame frome the video 
		current_frame = video_stream.read()
		current_frame = imutils.resize(current_frame, width=400)

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
			# keep looping if there is not an availiable out_frame
			if out_frame is None:
				continue

			(flag, encodedImage) = cv2.imencode(".jpg", out_frame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

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

	# start the flask app
	app.run(host=HOST_IP, port=HOST_PORT, debug=True,
		threaded=True, use_reloader=False)
		
	# create a single daemon thread for detecting motion
	motion_thread = threading.Thread(target=DetectMotion, args=(BACKGROUND_FRAME_COUNT_DEFAULT))
	motion_thread.daemon = True
	motion_thread.start()

# release the video stream pointer
video_stream.stop()