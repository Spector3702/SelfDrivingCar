import pygame as py
from config_variables import *
from car import decodeCommand
from vect2d import vect2d
from node import *

py.font.init()#pygame剛開始的initial

class NN:

    def __init__(self, config, genome, pos):
        self.input_nodes = []                               #input layers 的nodes
        self.output_nodes = []                              #output layers的 nodes
        self.nodes = []                                     #node
        self.genome = genome                                #基因組(?)
        self.pos = (int(pos[0]+NODE_RADIUS), int(pos[1]))   #位置=(原本x座標加上轉向=, y座標(因為車子不會上下動))
        input_names = ["Sensor T", "Sensor TR", "Sensor R", "Sensor BR", "Sensor B", "Sensor BL", "Sensor L", "Sensor TL", "Speed"]#input nodes的名字
        output_names = ["Accelerate", "Brake", "Turn Left", "Turn Right"]#output nodes的名字
        middle_nodes = [n for n in genome.nodes.keys()]     #基因組的key
        nodeIdList = []

        #nodes
        h = (INPUT_NEURONS-1)*(NODE_RADIUS*2 + NODE_SPACING)#input layers 的nodes 高度
        for i, input in enumerate(config.genome_config.input_keys):
            n = Node(input, pos[0], pos[1]+int(-h/2 + i*(NODE_RADIUS*2 + NODE_SPACING)), INPUT, [GREEN_PALE, GREEN, DARK_GREEN_PALE, DARK_GREEN], input_names[i], i)#Nodes construction function (id:input,x座標:pos[0],y座標:pos[1]加上原形直徑加上點跟點之間的距離,type:INPUT,color:[那四個],label:上述input name第幾個,index:第幾個)
            self.nodes.append(n)    #將input的nodes append進nodes內
            nodeIdList.append(input)#將這些index存進nodeIdList中

        h = (OUTPUT_NEURONS-1)*(NODE_RADIUS*2 + NODE_SPACING)#output layers的node高度
        for i,out in enumerate(config.genome_config.output_keys):
            n = Node(out+INPUT_NEURONS, pos[0] + 2*(LAYER_SPACING+2*NODE_RADIUS), pos[1]+int(-h/2 + i*(NODE_RADIUS*2 + NODE_SPACING)), OUTPUT, [RED_PALE, RED, DARK_RED_PALE, DARK_RED], output_names[i], i)#Nodes construction function (id:output,x座標:pos[0]加上input layer與output layer 之間的距離加上直徑,y座標:pos[1]加上原形直徑加上點跟點之間的距離,type:INPUT,color:[那四個],label:上述input name第幾個,index:第幾個)
            self.nodes.append(n)    #將output的nodes append進nodes內
            middle_nodes.remove(out)#每次就remove掉一個可能的基因組(?)
            nodeIdList.append(out)  #將這些index存進nodeIdList中

        h = (len(middle_nodes)-1)*(NODE_RADIUS*2 + NODE_SPACING)#hidden layers的node高度
        for i, m in enumerate(middle_nodes):
            n = Node(m, self.pos[0] + (LAYER_SPACING+2*NODE_RADIUS), self.pos[1]+int(-h/2 + i*(NODE_RADIUS*2 + NODE_SPACING)), MIDDLE, [BLUE_PALE, DARK_BLUE, BLUE_PALE, DARK_BLUE])#Nodes construction function (id:middle,x座標:pos[0]加上input layer與output layer 之間的距離加上直徑,y座標:pos[1]加上原形直徑加上點跟點之間的距離,type:INPUT,color:[那四個])
            self.nodes.append(n)    #將middle的nodes append進nodes內
            nodeIdList.append(m)    #將這些index存進nodeIdList中

        #connections
        self.connections = []
        for c in genome.connections.values():
            if c.enabled:
                input, output = c.key
                self.connections.append(Connection(self.nodes[nodeIdList.index(input)],self.nodes[nodeIdList.index(output)], c.weight))#將connection擴充(nodes[這些index中是input的],nodes[這些index中是output的],weight)

    def draw(self, world):#畫nodes的連線
        for c in self.connections:
            c.drawConnection(world)
        for node in self.nodes:
            node.draw_node(world)































#----
