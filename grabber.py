
import cv2
import win32api, win32con, win32ui, win32gui
import numpy as np
import threading
import time
import random
import dxcam


import clr
# change this to wherever your built DLL is
clr.AddReference('C:\\Users\\andre\\Desktop\\quiz-facilitator-main\\Python color\\REWORKED\\ClassLibrary1.dll')
# reminder all 3 dlls have to be in the same folder
from ClassLibrary1 import Class1
ud_mouse = Class1()
#ud_mouse.Run_Me()

# higher then 290 breaks the thing or sum idk
fov = 180

# lower to get more fps but worse performance
fps = 75
        

     

left, top = (1920 - fov) // 2, (1080 - fov) // 2
right, bottom = left + fov, top + fov
region = (left, top, right, bottom)
camera = dxcam.create(region=region, output_color="RGB")
camera.start(target_fps=fps, video_mode=True)
time.sleep(1)
    


class Grabber:
    def __init__(self, x_multiplier, y_multiplier, y_difference, flick_speed) -> None:
        # self.lower = np.array([139, 96, 129], np.uint8)
        # self.upper = np.array([169, 255, 255], np.uint8)
        self.lower = np.array([139, 95, 154], np.uint8)
        self.upper = np.array([153, 255, 255], np.uint8)
        self.x_multiplier = x_multiplier         # multiplier on x-coordinate
        self.y_multiplier = y_multiplier         # multiplier on y-coordinate
        self.y_difference = y_difference         # the amount of pixels added to the y-coordinate (aims higher)
        self.flick_speed = flick_speed

    def build_title(self, length) -> str:
        """return a randomly generated window title to prevent detections"""
        chars = [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '@', '#',
            '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '/', '?'
        ]
        return ''.join(random.choice(chars) for character in range(length))
    def find_dimensions(self, box_size): 
        """Calculates constants required for the bot."""
        self.box_size = box_size
        self.box_middle = int(self.box_size / 2) 
        top = int(((1080 / 2) - (self.box_size / 2))) 
        left = int(((1920 / 2) - (self.box_size / 2))) 
        self.dimensions = ( left,  top, left + self.box_size, top + self.box_size)
        
    def capture_frame(self): 
        return np.array(camera.get_latest_frame())
        # with mss() as sct:    
        #return np.array(sct.grab(self.dimensions))
    def process_frame(self, frame):
        """Performs operations on a frame to improve contour detection."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        processed = cv2.inRange(hsv, self.lower, self.upper)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, np.ones((10, 10), np.uint8))
        dilatation_size = 15
        # dilation_shape = cv2.MORPH_RECT
        # dilation_shape = cv2.MORPH_ELLIPSE
        dilation_shape = cv2.MORPH_CROSS
        element = cv2.getStructuringElement(dilation_shape, (2 * dilatation_size + 1, 2 * dilatation_size + 1),
                                    (dilatation_size, dilatation_size))
        processed = cv2.dilate(processed, element)
        processed = cv2.blur(processed, (8, 8))
        return processed
    def detect_contours(self, frame, minimum_size):
        """Returns contours larger then a specified size in a frame."""
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = []
        if len(contours) != 0:
            for i in contours:
                if ud_mouse.Check(cv2.contourArea(i), minimum_size):
                 #if cv2.contourArea(i) > minimum_size:
                    large_contours.append(i)
        return large_contours
    def compute_centroid(self, contour):
        """Returns x- and y- coordinates of the center of the largest contour."""
        c = max(contour, key=cv2.contourArea)
        rectangle = np.int0(cv2.boxPoints(cv2.minAreaRect(c)))
        new_box = []
        for point in rectangle:
            point_x = point[0]
            point_y = point[1]
            new_box.append([round(point_x, -1), round(point_y, -1)])
        M = cv2.moments(np.array(new_box))
        if M['m00']:
            center_x = (M['m10'] / M['m00'])
            center_y = (M['m01'] / M['m00'])
            x = -(self.box_middle - center_x)
            y = -(self.box_middle - center_y)
            return [], x, y
    def is_activated(self, key_code) -> bool:
        return ud_mouse.is_activated(key_code)

    def flick_mouse(self, x, y):
        threading.Thread(target=self._move_mouse, args=[x, y, self.x_multiplier*self.flick_speed, self.y_multiplier*(self.flick_speed/2), self.y_difference]).start()

    def move_mouse(self, x, y):
        threading.Thread(target=self._move_mouse, args=[x, y, self.x_multiplier, self.y_multiplier, self.y_difference]).start()

    def _move_mouse(self, x, y, x_multiplier, y_multiplier, y_difference):
        ud_mouse.move_mouse(x, y, self.box_size, x_multiplier, y_multiplier, y_difference)

    def click(self):
        threading.Thread(target=self._click).start()

    def trigger(self, x, trigger_sleep, trigger_hitbox):
        #while True:
            if x <= trigger_hitbox and x>=0:
                 threading.Thread(target=self._click).start()
                 #time.sleep(trigger_sleep)
            else:
                 if x >= -(trigger_hitbox) and x<=0:
                    threading.Thread(target=self._click).start()
                   #time.sleep(trigger_sleep)

    def flick_trigger(self, x, flick_sleep, flick_hitbox):
        #while True:
            if x <= flick_hitbox + flick_hitbox and x>=0:
                 threading.Thread(target=self._click).start()
                 #time.sleep(flick_sleep)
            else:
                 if x >= -(flick_hitbox)-flick_hitbox and x<=0:
                    threading.Thread(target=self._click).start()
                    #time.sleep(flick_sleep)

    def _click(self):        
        ud_mouse.click_mouse()
    


