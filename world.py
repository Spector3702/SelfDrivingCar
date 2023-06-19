import pygame as py

class World:

    initialPos = (0,0) # 原始位置初始值
    bestCarPos = (0,0) # 目標位置初始值

    def __init__(self, starting_pos, world_width, world_height):
        self.initialPos = starting_pos                               # 設定初始位置
        self.bestCarPos = (0, 0)                                     # 目標位置初始值
        self.win  = py.display.set_mode((world_width, world_height)) # 設定並創建視窗
        self.win_width = world_width                                 # world_width = WIN_WIDTH = 1350
        self.win_height = world_height                               # world_height = WIN_HEIGHT = 750
        self.score = 0                                               # 分數設定
        self.bestGenome = None                                       # ???
        self.save = 0
    def updateBestCarPos(self, pos): #位置存取
        self.bestCarPos = pos

    def getScreenCoords(self, x, y): #取得相對位置
        return (int(x + self.initialPos[0] - self.bestCarPos[0]), int(y + self.initialPos[1] - self.bestCarPos[1]))

    def getBestCarPos(self):
        return self.bestCarPos       #取得位置

    def updateScore(self, new_score):#更新成績
        self.score = new_score

    def getScore(self):              #取得成績
        return self.score
    
    def saveScore(self, score):
        self.save = score
    
    def getSave(self):
        return self.save
    