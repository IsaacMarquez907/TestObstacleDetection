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

# global variable for threshold value on subtraction of image
T_VAL = 127

# global variable for how many frames to hold in the history
HISTORY_SIZE = 150

# //////////////////////////////////////////////////
# Public Methods
# //////////////////////////////////////////////////

# //////////////////////////////////////////////////
# Public Classes
# //////////////////////////////////////////////////

# -- Public class to detect moving objects in a frame --
class MotionDetector:

	# initilize the member variables for this class
	def __init__(self):
		# kernel for morphological operation. 
		self.kernel = np.ones((20,20),np.uint8)

		# Create the background subtractor object
		self.background_model = cv2.createBackgroundSubtractorMOG2(history=HISTORY_SIZE,
			varThreshold=T_VAL, detectShadows=False)

	# Update the background model with a new frame.
	# This function will perform the following
	#	1. subtract current frame from the background
	#	2. convert the frame into a binary image
	#	3. Update the background model
	def UpdateBG(self, frame):
		# process the frame
		processed_frame = self.background_model.apply(frame)

		# return the processed frame
		return processed_frame

	# detect any motion within the passed in frame
	def DetectMotion(self, frame):
		# Process the passed in frame against the background model.
		# see function header of UpdateBG for more details
		processed_frame = self.UpdateBG(frame)

		# remove internal gaps using OpenCV's closing operation
		processed_frame = cv2.morphologyEx(processed_frame, cv2.MORPH_CLOSE, self.kernel)

		# remove image noise using OpenCV's median blur
		processed_frame = cv2.medianBlur(processed_frame, 5)

		# find motion by finding the contours within the image
		contours, hierarchy = cv2.findContours(processed_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		areas = [cv2.contourArea(c) for c in contours]

		# return the contours and areas found
		return (contours, areas)