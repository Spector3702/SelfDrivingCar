from config_variables import *
import pygame as py
import numpy as np
from scipy import interpolate
from math import *
from vect2d import * 
from random import random, seed

class Road:
    def __init__(self, world):
        self.num_ctrl_points = (int)((world.win_height+SAFE_SPACE)/SPACING)+2 
        # SPACING = 200 
        # SAFE_SPACE = SPACING + 50 = 250
        # world.win_height = WIN_HEIGHT = 750
        # => ((750+250)/200)+2 = 7 
        # self.num_ctrl_points = 7 ?

        self.last_ctrl_point = 0
        self.ctrl_points = []
        self.centerPoints = []
        self.pointsLeft = []
        self.pointsRight = []

        for i in range(self.num_ctrl_points):
             self.ctrl_points.append(vect2d()) # 新增向上的向量

        for i in range(NUM_POINTS*self.num_ctrl_points): 
            # 填充 pointsLeft 和 pointsRight 向量
            # NUM_POINTS  = 15                
            # number of points for each segment
            # NUM_POINTS*self.num_ctrl_points = 15*7 = 105

            self.pointsLeft.append(vect2d(1000,1000))  # 新增向量(1000,1000)
            self.pointsRight.append(vect2d(1000,1000)) # 新增向量(1000,1000)
            self.centerPoints.append(vect2d(1000,1000))# 新增向量(1000,1000)

        self.ctrl_points[0].co(0, SPACING) # (0,200)       # 將前兩個 control_points 初始化為直線
        self.ctrl_points[1].co(0, 0)       # (0,0)
        for i in range(NUM_POINTS):        # NUM_POINTS  = 15 
            x = self.ctrl_points[0].x
            y = self.ctrl_points[0].y - SPACING/NUM_POINTS*i # SPACING/NUM_POINTS = 200/15
            self.centerPoints[i].co(x, y)                    # 路徑座標
            self.pointsLeft[i].co(x - ROAD_WIDTH/2, y)       # 路徑左側邊界座標
            self.pointsRight[i].co(x + ROAD_WIDTH/2, y)      # 路徑右側邊界座標
        self.next_point = NUM_POINTS

        for i in range(self.num_ctrl_points-2): # range(5)
            self.createSegment(i+1)

        self.last_ctrl_point = self.num_ctrl_points-1
        self.bottomPointIndex = 0

    def calcBorders(self, i): # 計算當前路徑邊界
        prev_index = getPoint(i-1, self.num_ctrl_points*NUM_POINTS)
        center = self.centerPoints[i]
        prev = self.centerPoints[prev_index]
        angle = atan2(center.x-prev.x, prev.y-center.y)

        x = ROAD_WIDTH/2 * cos(angle) # 三角函數算實際距離
        y = ROAD_WIDTH/2 * sin(angle) # 三角函數算實際距離
        self.pointsLeft[i].x = center.x - x  # 路徑左側邊界座標
        self.pointsLeft[i].y = center.y - y if not center.y - y >= self.pointsLeft[prev_index].y else self.pointsLeft[prev_index].y
        self.pointsRight[i].x = center.x + x # 路徑右側邊界座標
        self.pointsRight[i].y = center.y + y if not center.y + y >= self.pointsRight[prev_index].y else self.pointsRight[prev_index].y

    def createSegment(self, index):
        p1 = self.ctrl_points[getPoint(index, self.num_ctrl_points)]    # 猜測為準備要生成的point1
        p2 = self.ctrl_points[getPoint(index+1, self.num_ctrl_points)]  # 猜測為準備要生成的point2

        #define p2
        seed()
        p2.co(p1.x + (random()-0.5)*MAX_DEVIATION, p1.y-SPACING)
        p2.angle = MAX_ANGLE*(random()-0.5)

        y_tmp = []
        for i in range(NUM_POINTS):
            y_tmp.append(p2.y+SPACING/NUM_POINTS*i)

        #get cubic spline of the center line of the road
        ny = np.array([p2.y, p1.y]) #反轉是因為 scify 想要增加 x（在本例中是 y）
        nx = np.array([p2.x, p1.x])
        cs = interpolate.CubicSpline(ny, nx, axis=0, bc_type=((1,p2.angle),(1,p1.angle))) 
        # cubic spline 用來畫出光滑形狀的工具 

        res = cs(y_tmp)
        
        #create the actual borders
        for i in range(NUM_POINTS):
            self.centerPoints[self.next_point].x = res[NUM_POINTS-i-1]
            self.centerPoints[self.next_point].y = y_tmp[NUM_POINTS-i-1]
            self.calcBorders(self.next_point)

            self.next_point = getPoint(self.next_point+1, NUM_POINTS*self.num_ctrl_points)

        self.last_ctrl_point = getPoint(self.last_ctrl_point+1, self.num_ctrl_points)
        self.bottomPointIndex = self.next_point

    def update(self, world):
        if world.getScreenCoords(0, self.ctrl_points[self.last_ctrl_point].y)[1] > -SAFE_SPACE:
            self.createSegment(self.last_ctrl_point)


    def draw(self, world,ROAD_DBG):
        #draw control_points, 邊界 = 點(藍色)
        if(ROAD_DBG): 

            #for p in self.ctrl_points:     #EEEEEEEEEEEEEEEEE
                #py.draw.circle(win, BLUE, (int(p.x), int(p.y)), 4)
            # 上面兩行是他原本的 應該只是範例

            for i in range(len(self.pointsLeft)):
                next_index = getPoint(i+1, NUM_POINTS*self.num_ctrl_points)
                py.draw.circle(world.win, WHITE, world.getScreenCoords(self.pointsLeft[i].x, self.pointsLeft[i].y), 2)
                py.draw.circle(world.win, WHITE, world.getScreenCoords(self.pointsRight[i].x, self.pointsRight[i].y), 2)
                if i%3==0:
                    py.draw.line(world.win, GREEN_PALE, world.getScreenCoords((self.pointsRight[i].x+self.pointsLeft[i].x)/2, (self.pointsRight[i].y+ self.pointsLeft[i].y)/2),world.getScreenCoords((self.pointsRight[next_index].x+self.pointsLeft[next_index].x)/2, (self.pointsRight[next_index].y+ self.pointsLeft[next_index].y)/2), 2)
                #py.draw.lines(win, BLACK, False, [(self.pointsLeft[i].x, self.pointsLeft[i].y), (self.pointsRight[i].x, self.pointsRight[i].y)], 1)
        else:
            #draw borders, 邊界 = 線條 
            for i in range(len(self.pointsLeft)):
                next_index = getPoint(i+1, NUM_POINTS*self.num_ctrl_points)

                p1 = self.pointsLeft[i]           # p = previous
                f1 = self.pointsLeft[next_index]  # f = future
                if p1.y >= f1.y:
                    py.draw.line(world.win, WHITE, world.getScreenCoords(p1.x, p1.y), world.getScreenCoords(f1.x, f1.y), 4)
                    py.draw.line(world.win, GRAY, world.getScreenCoords(p1.x-10, p1.y), world.getScreenCoords(f1.x-10, f1.y), 4)                    
                    py.draw.line(world.win, YELLOW, world.getScreenCoords(p1.x, p1.y), world.getScreenCoords(f1.x+30, f1.y-20), 1)
                    #if p1.x <= f1.x:
                    #    py.draw.line(world.win, YELLOW, world.getScreenCoords(p1.x, p1.y), world.getScreenCoords(f1.x+30, f1.y-30), 1)
                    #else:
                    #    py.draw.line(world.win, YELLOW, world.getScreenCoords(p1.x, p1.y), world.getScreenCoords(f1.x-30, f1.y-30), 1)
                    # 畫左側道路邊界, 顏色 = 白, 寬度 = 4
                p2 = self.pointsRight[i]          # p = previous
                f2 = self.pointsRight[next_index] # f = future
                if p2.y >= f2.y: 
                    py.draw.line(world.win, WHITE, world.getScreenCoords(p2.x, p2.y),world.getScreenCoords(f2.x, f2.y), 4)
                    py.draw.line(world.win, GRAY, world.getScreenCoords(p2.x+10,p2.y),world.getScreenCoords(f2.x+10, f2.y), 4)
                    py.draw.line(world.win, YELLOW, world.getScreenCoords(p2.x, p2.y),world.getScreenCoords(f2.x-30, f2.y-20), 1)
                    #if p2.x >= p2.x:                  
                    #    py.draw.line(world.win, YELLOW, world.getScreenCoords(p2.x, p2.y),world.getScreenCoords(f2.x-30, f2.y-30), 1)
                    #else:
                    #    py.draw.line(world.win, YELLOW, world.getScreenCoords(p2.x, p2.y),world.getScreenCoords(f2.x+30, f2.y-30), 1)
                    # 畫右側道路邊界, 顏色 = 白, 寬度 = 4
                if i%5==0 or i%5==1:
                    py.draw.line(world.win, GRAY, world.getScreenCoords((self.pointsRight[i].x+self.pointsLeft[i].x)/2, (self.pointsRight[i].y+ self.pointsLeft[i].y)/2),world.getScreenCoords((self.pointsRight[next_index].x+self.pointsLeft[next_index].x)/2, (self.pointsRight[next_index].y+ self.pointsLeft[next_index].y)/2), 4)


def getPoint(i, cap):
    return (i+cap)%cap









    #持續更新中
