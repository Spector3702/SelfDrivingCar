import pygame as py
import os
from config_variables import *

class SW:
    def __init__(self):
        self.image = py.transform.scale(py.image.load(os.path.join('steering_wheel.png')).convert_alpha(),(SW_IMG_SIZE,SW_IMG_SIZE))
        self.rect = (0,0)
        self.angle = -BEST_CAR_ROTATION*3
    def rotate(self):
        self.image = py.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center = self.rect.center)
        
