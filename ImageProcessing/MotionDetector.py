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
import numpy 
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
			self.background = frame.copy().astype("float")
			return
		
		# convert the image to grayscale and blur it to reduce noise
		processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		processed_frame = cv2.GaussianBlur(processed_frame, (7,7), 0)

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
		image_difference = cv2.absdiff(self.background.astype("uint8"), frame)
		binary_image = cv2.threshold(image_difference, tVal, 255, cv2.THRESH_BINARY)[1]

		# isolate objects and remove noise using erode and dilate
		# within the opencv library
		binary_image = cv2.erode(binary_image, None, iterations=3)
		binary_image = cv2.dilate(binary_image, None, iterations=3)

		#find the contours within the image to localize motion
		contours = cv2.findContours(binary_image.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		contours = imutils.grab_contours(contours)

		# if there were contours, find the largest bounding box
		if len(contours) != 0:
			# loop over the contours and find the largest bounding box
			# aslo initilize Start and end coordinates as infinity and negative infinity
			(startX, startY) = (numpy.inf, numpy.inf)
			(endX, endY) = (-numpy.inf, -numpy.inf)
			for current_contour in contours:
				# compute the current bounding box
				(x, y, w, h) = cv2.boundingRect(current_contour)

				# if it is larger then the previous bounding box
				# store it the start and end coordinates
				(startX,startY) = (min(startX, x), min(startY, y))
				(endX, endY) = (max(endX, x + w), max(endY, y + h))

			# return the largest bounding box
			return (startX, startY, endX, endY)
		else:
			# else => return None
			return None