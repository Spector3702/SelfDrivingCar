import pygame as py
py.font.init()


#=================== General constants ==================================
FPS = 30
WIN_WIDTH = 1350
WIN_HEIGHT = 750
STARTING_POS = (WIN_WIDTH/2, WIN_HEIGHT-100)
SCORE_VEL_MULTIPLIER = 0.00       #bonus for faster cars
BAD_GENOME_TRESHOLD = 200                       #if a car is too far behind it is removed

INPUT_NEURONS = 9
OUTPUT_NEURONS = 4

#=================== Car Specs ==================================

CAR_DBG = False
FRICTION  = -0.1
MAX_VEL = 10
MAX_VEL_REDUCTION = 1              #at the start reduce maximum speed
ACC_STRENGHT = 0.2
BRAKE_STREGHT = 1
TURN_VEL = 2
SENSOR_DISTANCE = 1000
ACTIVATION_TRESHOLD = 0.5

#=================== Road Specs ==================================

ROAD_DBG = False
MAX_ANGLE = 1       # 1
MAX_DEVIATION = 1800 # 1900
SPACING = 800      # 200
NUM_POINTS  = 90   # 15        # number of points for each segment
SAFE_SPACE = SPACING + 50       # buffer space above the screen
ROAD_WIDTH = 180

#=================== Display and Colors ==================================

NODE_RADIUS = 20
NODE_SPACING = 5
LAYER_SPACING = 100
CONNECTION_WIDTH = 1

WHITE = (255, 255, 255)
BRIGHT_GRAY = (200,200,200)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BRIGHT_RED = (255,0,0)
DARK_RED = (100, 0, 0)
RED_PALE = (250, 200, 200)
DARK_RED_PALE = (150, 100, 100)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0)
GREEN_PALE = (200, 250, 200)
DARK_GREEN_PALE = (100, 150, 100)
BLUE = (0,0,255)
BLUE_PALE = (200, 200, 255)
DARK_BLUE = (100, 100, 150)
YELLOW = (200,200,0,123)

NODE_FONT = py.font.SysFont("comicsans", 15)
STAT_FONT = py.font.SysFont('bahnschrift', 50)
STAT_FONT_1 = py.font.SysFont('bahnschrift', 30)
STAT_FONT_2 = py.font.SysFont('bahnschrift', 15)
#=================== Constants for internal use ==================================
GEN = 0

MAX_GEN = 500
GEN_INTERVAL = 2
ISTEST = False # 是否為測試模式

BS = 0
SCALE = 0.2
PRE_TIME_R = 0
PRE_TIME_C = 0

BEST_CAR_VEL = 0
BEST_CAR_STATUS = [0,0,0,0]
BEST_CAR_ROTATION = 0

EX_IMG_SIZE_Y = 300
EX_IMG_SIZE_X = int(EX_IMG_SIZE_Y*1.11)

EX_IMG_POS_X = 1000
EX_IMG_POS_Y = 230

SW_IMG_SIZE = 50
SW_IMG_POS_X = 1090
SW_IMG_POS_Y = 600
#enumerations
ACC = 0
BRAKE = 1
TURN_LEFT = 2
TURN_RIGHT = 3

INPUT = 0
MIDDLE = 1
OUTPUT = 2
