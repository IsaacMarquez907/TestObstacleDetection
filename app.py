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
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2

# //////////////////////////////////////////////////
# Global constants
# //////////////////////////////////////////////////

# gobal variable used to store the current output frame for the website
output_frame = None

# global variable for the flask application
app = Flask(__name__)

# global variable for the video stream
video_stream = VideoStream(usePiCamera=1).start()
time.sleep(2.0) # warm-up the camera

# global variables to store the host ip and port number
HOST_IP   = '192.168.1.17'
HOST_PORT = '5000'

# //////////////////////////////////////////////////
# Public Routes and Methods
# //////////////////////////////////////////////////

# route the home page to render index.html
@app.route("/")
def index():
    return render_template("index.html")

# //////////////////////////////////////////////////
# Initialize the Camera and Frame Displayer
# //////////////////////////////////////////////////

# //////////////////////////////////////////////////
# Main Method
# //////////////////////////////////////////////////

# -- Main Method to start the flask app -- 
if __name__ == '__main__':

	# start the flask app
	app.run(host=HOST_IP, port=HOST_PORT, debug=True,
		threaded=True, use_reloader=False)
		
# release the video stream pointer
video_stream.stop()