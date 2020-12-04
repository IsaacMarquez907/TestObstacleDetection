#!/usr/bin/env python3

##
# @file MotionDetector.py
#
# @brief Python class to store weighted value 
#           of past frames, and detect motion using
#           subtractive algorithms
# @details 
#         Author: Isaac Marquez
#         Obstacle Avoidance on RPI4
#         OpenCV 4.4.0
#         November, 2020

# //////////////////////////////////////////////////
# Import the necessary packages
# //////////////////////////////////////////////////
import numpy as np
import imutils
import cv2

# //////////////////////////////////////////////////
# Global constants
# //////////////////////////////////////////////////

# global variable for the weighted value of the background
# and the incoming frame
WEIGHT = 0.5

# //////////////////////////////////////////////////
# Public Classes
# //////////////////////////////////////////////////

# -- Public class to detect moving objects in a frame --
class MotionDetector:

	# initilize the background model for this class
	def __init__(self, weight=0.5):
		# initialize the background model to NULL   
		self.background = None

	# update the background model with a new frame
	def UpdateBG(self, frame):
		# if there has been no frames yet
		# initialize the background to the current frame
		if self.background is None:
			self.background = frame.cop().astype("float")
			return
		
		# otherwise update the background model by taking
		# the weighted average with configurable weight
		cv2.accumulateWeighted(frame, self.background, WEIGHT)

	# detect any motion within the passed in frame
	def DetectMotion(self, frame, tVal=25):
		# convert the image to grayscale and blur it to reduce noise
		processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		processed_frame = cv2.GaussianBlur(processed_frame, (7,7), 0)

	        # compute the difference of the passed in frame against the
                # the background model. Then take the threshold of image so 
                # that it is now a binary image with either white or black
                # pixels
                    image_difference = cv

		
