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
# Public Classes 
# //////////////////////////////////////////////////

# --- Class to Take in Frames and display them to the user ---
class FrameDisplayer:
    def __init__(self):
        print ("init") 
    
    # Display the passed in frame
    def DisplayFrame(self, frame):
        # dipslay the frame
        cv2.imshow('Frame',frame)
        
        # Clear the stream in preparation for the next frame
        raw_capture.truncate(0)

    # Display the passed in frame with a bounding box
    def DisplayFrameWithBoundingBox(self, frame, areas):
                 
        # Find the largest moving object in the image
        max_index = np.argmax(areas)
           
        # Draw the bounding box
        cnt = contours[max_index]
        x,y,w,h = cv2.boundingRect(cnt)
        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),3)

        # Draw circle in the center of the bounding box
        x2 = x + int(w/2)
        y2 = y + int(h/2)
        cv2.circle(image,(x2,y2),4,(0,255,0),-1)

        # Print the centroid coordinates (we'll use the center of the
        # bounding box) on the image
        text = "x: " + str(x2) + ", y: " + str(y2)
        cv2.putText(image, text, (x2 - 10, y2 - 10),
          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
              
        # Display the resulting frame
        cv2.imshow("Frame",image)
        
        # Clear the stream in preparation for the next frame
        raw_capture.truncate(0)
 
# //////////////////////////////////////////////////
# Initialize the Camera and Frame Displayer
# //////////////////////////////////////////////////
camera = PiCamera()
FrameDisplayer = FrameDisplayer()
 
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

# //////////////////////////////////////////////////
# Main Method
# //////////////////////////////////////////////////
# Capture frames continuously from the camera
for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
    
    # Stop capturing frames once the user has hit the q key on the keyboard
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
     
    # Grab the raw NumPy array representing the image
    image = frame.array
 
    # Convert to foreground mask
    fg_mask = back_sub.apply(image)
     
    # Close gaps using closing
    fg_mask = cv2.morphologyEx(fg_mask,cv2.MORPH_CLOSE,kernel)
       
    # Remove salt and pepper noise with a median filter
    fg_mask = cv2.medianBlur(fg_mask,5)
       
    # If a pixel is less than ##, it is considered black (background). 
    # Otherwise, it is white (foreground). 255 is upper limit.
    # Modify the number after fg_mask as you see fit.
    _, fg_mask = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)
 
    # Find the contours of the object inside the binary image
    contours, hierarchy = cv2.findContours(fg_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:]
    areas = [cv2.contourArea(c) for c in contours]
  
    # If there are no countours
    if len(areas) < 1:
        # Draw the frame without a bounding box
        FrameDisplayer.DisplayFrame(image)
    else:
        # Draw the frame without a bounding box
        FrameDisplayer.DisplayFrameWithBoundingBox(image, areas)
        

 
# Close down windows
cv2.destroyAllWindows()