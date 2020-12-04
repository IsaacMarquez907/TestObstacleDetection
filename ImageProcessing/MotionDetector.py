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

# //////////////////////////////////////////////////
# Public Classes
# //////////////////////////////////////////////////

# -- Public class to detect moving objects in a frame --
class MotionDetector:

    # initilize the accumlated weight variable to default 0.5
    def __init__(self, weight=0.5):
		# store the accumulated weight factor
        self.weight = weight
		# initialize the background model to NULL   
        self.background = None