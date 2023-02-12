import pygame as py
from car import decodeCommand
from config_variables import *

class Node:
    def __init__(self, id, x, y, type, color, label = "", index=0):
        self.id = id            # 從config拿input_keys，不確定是啥
        self.x = x              # x座標
        self.y = y              # y座標
        self.type = type        # 輸入|中間層|輸出
        self.color = color      # 顏色[4]
        self.label = label      # 標籤(名稱)
        self.index = index      # 索引值，當output時 = ACC|BRAKE|TURN_LEFT|TURN_RIGHT

    def draw_node(self, world):
        # 取得2*3顏色矩陣
        colorScheme = self.getNodeColors(world)

        py.draw.circle(world.win, colorScheme[0], (self.x,self.y), NODE_RADIUS)     # 畫圓的邊 (深色)
        py.draw.circle(world.win, colorScheme[1], (self.x,self.y), NODE_RADIUS-2)   # 畫圓內部 (淺色)

        # draw labels
        if self.type != MIDDLE:
            text = NODE_FONT.render(self.label, 1, WHITE)
            world.win.blit(text, (self.x + (self.type-1) * ((text.get_width() if not self.type else 0) + NODE_RADIUS + 5), self.y - text.get_height()/2))

    # 取得顏色的2*3矩陣
    def getNodeColors(self, world):
        # 判斷是什麼層
        if self.type == INPUT:                                                  # 若是輸入層
            ratio = world.bestInputs[self.index]                                # bestInputs 宣告在main中 = sensors正規化的inputs(0~1)
        elif self.type == OUTPUT:                                               # 若是輸出層
            ratio = 1 if decodeCommand(world.bestCommands, self.index) else 0   # 指令有效就 = 1，否則 = 0
        else:                                                                   # 若是中間層
            ratio = 0                                                           # 就等於0

        # 計算顏色的rgb
        col = [[0,0,0], [0,0,0]]
        for i in range(3):                                                                  # 根據深淺顏色比例，計算最後的顏色深淺
            col[0][i] = int(ratio * (self.color[1][i]-self.color[3][i]) + self.color[3][i]) # 1, 3是飽和的顏色 (圓的邊)
            col[1][i] = int(ratio * (self.color[0][i]-self.color[2][i]) + self.color[2][i]) # 0, 2是粉色系 (圓的內部顏色)
        
        return col

# Node間的那些線
class Connection:
    def __init__(self, input, output, wt):
        self.input = input      # input node
        self.output = output    # output node
        self.wt = wt            # weight

    def drawConnection(self, world):
        color = GREEN if self.wt >= 0 else RED          # 權重為正 = 綠色，否則紅色
        width = int(abs(self.wt * CONNECTION_WIDTH))    # |權重|和線寬成正比
        py.draw.line(world.win, color, (self.input.x + NODE_RADIUS, self.input.y), (self.output.x - NODE_RADIUS, self.output.y), width)
