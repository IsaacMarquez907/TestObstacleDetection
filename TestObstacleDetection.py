#!/usr/bin/env python3

##
# @file TestObstacleDetection.py
#
# @brief Proof of concept for using Pi4, Pi camera v1,
#         and OpenCV to detect moving objects
#
# @details 
#         Author: Isaac Marquez
#         Obstacle Avoidance on RPI4
#         OpenCV 4.4.0
#         November, 2020


# //////////////////////////////////////////////////
# Import the necessary packages
# //////////////////////////////////////////////////
from picamera.array import PiRGBArray  # Needed to access the raw video stream of the Raspberry pi
from picamera import PiCamera          # Provides a Python interface for the RPi Camera Module
import time                            # Provides time-related functions
import cv2                             # OpenCV library
import numpy as np                     # Import NumPy library
 
 
# //////////////////////////////////////////////////
# Global constants
# //////////////////////////////////////////////////
# the resolution of the camera and frame rate
CAMERA_WIDTH  =            640
CAMERA_HEIGHT =            480
CAMERA_FRAME_RATE =         30 

 
# //////////////////////////////////////////////////
# Initialize the Camera
# //////////////////////////////////////////////////
camera = PiCamera()
 
# Set the camera resolution -- the smaller the faster
# the processing => i use a 640 x 480 window
camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
 
# Set the framerate of the camera
camera.framerate = CAMERA_FRAME_RATE
 
# Link up the raw fed of data coming from the camera
raw_capture = PiRGBArray(camera, size=(CAMERA_WIDTH, CAMERA_HEIGHT))
 
# Create the background subtractor object
back_sub = cv2.createBackgroundSubtractorMOG2(history=150,
  varThreshold=25, detectShadows=True)
 
# Wait a 0.1 seconds to allow the camera time to warmup
time.sleep(0.1)
 
# Create kernel for morphological operation. You can tweak
# the dimensions of the kernel.
# e.g. instead of 20, 20, you can try 30, 30
kernel = np.ones((20,20),np.uint8)