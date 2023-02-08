from config_variables import *
import pygame as py
import os
from math import *
from random import random
from road import *
import numpy as np
from vect2d import vect2d


class Car:
    x = 0
    y = 0       # (谷哥翻譯)坐標相對於全球參考系，屏幕上的位置是相對於最佳機器位置

    # called every time an object is created from a class
    # Car 有三個參數 : (x, y, turn)
    def __init__(self, x, y, turn):
        # 宣告變數
        self.x = x                  # x座標
        self.y = y                  # y座標
        self.rot = turn             # 轉向
        self.rot = 0                # 轉向初始使為0 (?)
        self.vel = MAX_VEL/2        # 速度
        self.acc = 0                # 加速度
        self.initImgs()             # 圖片設定初始
        self.commands = [0,0,0,0]   # 指令(加速、煞車、左轉、右轉)

    # 初始圖片設定
    def initImgs(self):
        # 隨機選一種顏色的車圖片
        img_names = ["yellow_car.png", "red_car.png", "blu_car.png", "green_car.png"]
        name = img_names[floor(random()*len(img_names))%len(img_names)]

        # convert_alpha() : change the pixel format of an image including per pixel alphas
        # 存取圖片後，設定大小為120*69，並旋轉90度
        # name : 車身圖片 ； brake : 煞車燈圖片
        self.img = py.transform.rotate(py.transform.scale(py.image.load(os.path.join("imgs", name)).convert_alpha(), (120,69)), -90)
        self.brake_img = py.transform.rotate(py.transform.scale(py.image.load(os.path.join("imgs", "brakes.png")).convert_alpha(), (120,69)), -90)

    # 偵測碰撞
    def detectCollision(self, road):
        #get mask
        mask = py.mask.from_surface(self.img)
        (width, height) = mask.get_size()

        # road.pointsLeft : 儲存左邊所有點的陣列 ； road.pointsRight : 儲存右邊所有點的陣列
        # v : 讀取[road.pointsLeft, road.pointsRight]，第一個元素為road.pointsLeft，第二個為road.pointsRight
        for v in [road.pointsLeft, road.pointsRight]:
            for p in v:                         # p : for each point in v
                x = p.x - self.x + width/2      # 路邊線 - 車位置 + 一半車寬，小於車寬就會在mask內，也代表撞到了
                y = p.y - self.y + height/2     # 路邊線 - 車位置 + 一半車長，小於車長就會在mask內，也代表撞到了

                # 偵測到撞牆便回傳True
                try:
                    if mask.get_at((int(x),int(y))):    # get_at() : get the color value at a single pixel
                        return True
                except IndexError as error:
                    continue
        return False

    # 取得sensor的inputs
    def getInputs(self, world, road):
        sensors = []

        # 預設sensors[8]的距離 = 200
        for k in range(8):
            sensors.append(SENSOR_DISTANCE)

        # sensorsEquations = [(a0,b0,c0), (a1,b1,c1), (a2,b2,c2), (a3,b3,c3)]；取得直線方程的係數
        sensorsEquations = getSensorEquations(self, world)

        # 一樣先左再右，總共做兩次
        for v in [road.pointsLeft, road.pointsRight]:
            # 取得路底的index
            i = road.bottomPointIndex

            while v[i].y > self.y - SENSOR_DISTANCE:                                        # 若路的邊線(bottomPointIndex)在畫面中
                next_index = getPoint(i+1, NUM_POINTS*road.num_ctrl_points)                 # next_index = (i+1) % (15*num_ctrl_points)
                getDistance(world, self, sensors, sensorsEquations, v[i], v[next_index])    # 根據 (v[i], v[next_index]) 兩點更新sensors[8]的距離
                i = next_index

        # 畫出車的感測器；CAR_DBG = False 所以沒執行
        if CAR_DBG:
            for k,s in enumerate(sensors):
                omega = radians(self.rot + 45*k)    # 弧度(轉向 + 0, 45, ... , 45*7) ，分別是前跟後的四個sensor (大概每個差45度)
                dx = s * sin(omega)                 # dx = 距離 * sin；(畢氏定理，三角形的高)
                dy = - s * cos(omega)               # dy = -距離 * cos；(畢氏定理，三角形的底)

                # (谷哥翻譯) 繪製傳感器的交叉點
                if s < SENSOR_DISTANCE:
                    py.draw.circle(world.win, RED, world.getScreenCoords(self.x+dx, self.y+dy), 6)

        # convert to value between 0 (distance = max) and 1 (distance = 0)；正規化
        for s in range(len(sensors)):
            sensors[s] = 1 - sensors[s]/SENSOR_DISTANCE

        return sensors

    # 根據車速、轉向更新位置
    def move(self, road, t):
        # 加速初始為-0.1
        self.acc = FRICTION

        # 讀取指令並更新加速即轉向
        if decodeCommand(self.commands, ACC):
            self.acc = ACC_STRENGHT
        if decodeCommand(self.commands, BRAKE):
            self.acc = -BRAKE_STREGHT
        if decodeCommand(self.commands, TURN_LEFT):
            self.rot -= TURN_VEL
        if decodeCommand(self.commands, TURN_RIGHT):
            self.rot += TURN_VEL

        # 決定目前的最高速
        timeBuffer = 500    # 還不懂timebuffer的用意
        if MAX_VEL_REDUCTION == 1 or t >= timeBuffer:
            max_vel_local = MAX_VEL
        else:
            ratio = MAX_VEL_REDUCTION + (1 - MAX_VEL_REDUCTION)*(t/timeBuffer)
            max_vel_local = MAX_VEL *ratio

        # 更新車速
        self.vel += self.acc
        if self.vel > max_vel_local:
            self.vel = max_vel_local
        if self.vel < 0:
            self.vel = 0

        # 更新車的位置
        self.x = self.x + self.vel * sin(radians(self.rot))
        self.y = self.y - self.vel * cos(radians(self.rot)) # (谷哥翻譯) 減去是因為原點在左上角

        #print("coord: ("+str(self.x)+", "+str(self.y)+")   vel: "+str(self.vel)+"   acc: "+str(self.acc) + "    rot: "+str(self.rot))
        return (self.x, self.y)

    # 根據車的位置及轉向將車圖放上去
    def draw(self, world):
        screen_position = world.getScreenCoords(self.x, self.y)
        rotated_img = py.transform.rotate(self.img, -self.rot)
        new_rect = rotated_img.get_rect(center = screen_position)
        world.win.blit(rotated_img, new_rect.topleft)

        # 若煞車要加上煞車圖片
        if decodeCommand(self.commands, BRAKE):
            rotated_img = py.transform.rotate(self.brake_img, -self.rot)
            new_rect = rotated_img.get_rect(center = screen_position)
            world.win.blit(rotated_img, new_rect.topleft)

    #======================== LOCAL FUNCTIONS ==========================

# 取得四個感測器直線方程式的三個係數 [(a0,b0,c0), (a1,b1,c1), (a2,b2,c2), (a3,b3,c3)]
def getSensorEquations(self, world):
    eq = []
    for i in range(4):
        omega = radians(self.rot + 45*i)    # 弧度(轉向 + 0/45/90/135) ，分別是前跟後的四個sensor (大概每個差45度)
        dx = SENSOR_DISTANCE * sin(omega)   # dx = 200 * sin；(畢氏定理，三角形的高)
        dy = - SENSOR_DISTANCE * cos(omega) # dy = -200 * cos；(畢氏定理，三角形的底)

        # 畫車到感測器的線；CAR_DBG = False 所以沒執行
        if CAR_DBG:                         
            # pygame.draw.lines() : draw multiple contiguous straight line segments
            # lines(surface, color, closed, points, width=1)
            #       - closed (bool)         : if True an additional line segment is drawn between the first and last points in the points sequence
            #       - points (coordinate)   : for the points [(x1, y1), (x2, y2), (x3, y3)] a line segment will be drawn from (x1, y1) to (x2, y2) and from (x2, y2) to (x3, y3), 
            #                                  additionally if the closed parameter is True another line segment will be drawn from (x3, y3) to (x1, y1)
            py.draw.lines(world.win, GREEN, False, [world.getScreenCoords(self.x+dx, self.y+dy), world.getScreenCoords(self.x-dx, self.y-dy)], 2)

        coef = getSegmentEquation(self, vect2d(x = self.x+dx, y = self.y+dy))   # 取得 ax + by + c = 0 的 (a, b, c)三個係數，x & y分別為四個感測器的位置
        eq.append(coef)                                                         # 儲存係數進eq
    return eq

# (谷哥翻譯) 兩點之間變量 y 的方程（考慮到 y 倒置的坐標系），一般形式為 ax + by + c = 0
def getSegmentEquation(p, q):
    a = p.y - q.y
    b = q.x - p.x
    c = p.x*q.y - q.x*p.y
    # 式子完整表示 : (y1-y2)x + (x2-x1)y = -(x1*y2 - x2*y1)
    #            => (y1*x + x2*y) - (y2*x + x1*y) = x2*y1 - x1*y2
    return (a,b,c)

# (谷哥翻譯) 給定段 (m,q) 計算距離並將其放入相應的傳感器中
def getDistance(world, car, sensors, sensorsEquations, p, q):     
    (a2,b2,c2) = getSegmentEquation(p, q)   # 路邊線切線的係數

    for i,(a1,b1,c1) in enumerate(sensorsEquations): # sensorsEquations = [(a0,b0,c0), (a1,b1,c1), (a2,b2,c2), (a3,b3,c3)]
        # get intersection between sensor(a1 + b1 + c1 = 0) and (切線)segment(a2x + b2y + c2 = 0)
        if a1!=a2 or b1!=b2:    # 如果不是平行
            d = b1*a2 - a1*b2   # 行列式
            if d == 0:
                continue
            y = (a1*c2 - c1*a2)/d                              # 行列式解y
            x = (c1*b2 - b1*c2)/d                              # 行列式解x
            if (y-p.y)*(y-q.y) > 0 or (x-p.x)*(x-q.x) > 0:     # 若在 p,q 兩點之外
                continue                                       # 則進下個迴圈 
        else:                                                  # 如果平行
            (x, y) = (abs(p.x-q.x), abs(p.y-q.y))              # 卡

        # get distance
        dist = ((car.x - x)**2 + (car.y - y)**2)**0.5        # 畢氏定理(車到交點的距離)

        # (谷哥翻譯) 以正確的方向插入傳感器
        omega = car.rot + 45*i                                          # 轉向 + 0/45/90/135
        alpha = 90 - degrees(atan2(car.y - y, x - car.x))               # atan2(y, x) : Return the arc tangent of y/x in radians；取得相對位置的對角
        if cos(alpha)*cos(omega)*100 + sin(alpha)*sin(omega)*100 > 0:   # => cos(alpha - omega)*100 > 0 => cos(alpha - omega) > 0 (?) => -90 < alpha - omega < 90
            index = i                                                   # 車前的感測器
        else:                                                           # if 90 < alpha - omega < 270
            index = i + 4                                               # 車後的感測器

        # 如果感測器距離變短就更新
        if dist < sensors[index]:
            sensors[index] = dist

# 讀取指令，決定要不要執行
def decodeCommand(commands, type):
    if commands[type] > ACTIVATION_TRESHOLD:                                # ACTIVATION_TRESHOLD = 0.5
        if type == ACC and commands[type] > commands[BRAKE]:                # 若輸入為"前進"且"前進"比"煞車"多
            return True                                                     # 就前進
        elif type == BRAKE and commands[type] > commands[ACC]:              # 若輸入為"煞車"且"煞車"比"前進"多
            return True                                                     # 就煞車
        elif type == TURN_LEFT and commands[type] > commands[TURN_RIGHT]:   # 若輸入為"左轉"且"左轉"比"右轉"多
            return True                                                     # 就左轉
        elif type == TURN_RIGHT and commands[type] > commands[TURN_LEFT]:   # 若輸入為"右轉"且"右轉"比"左轉"多
            return True                                                     # 就右轉
    return False                                                            # 否則指令無效

    #----