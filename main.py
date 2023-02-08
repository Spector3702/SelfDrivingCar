import pygame as py
import neat
import time
import os
import random
from car import Car
from road import Road
from world import World
from NNdraw import NN
from config_variables import *
py.font.init()#初始化pygame


bg = py.Surface((WIN_WIDTH, WIN_HEIGHT))  #創建一個窗口，大小為WIN_WIDTH * WIN_HEIGHT
bg.fill(GRAY)                             #把此窗口填上灰色


def draw_win(cars, road, world, GEN):     #x 跟y 是最佳汽車的位置
    road.draw(world)                      #創建路與車
    for car in cars:
        car.draw(world)

    text = STAT_FONT.render("Best Car Score: "+str(int(world.getScore())), 1, BLACK)#顯示 Best Car Score 平滑且黑色
    world.win.blit(text, (world.win_width-text.get_width() - 10, 10))
    text = STAT_FONT.render("Gen: "+str(GEN), 1, BLACK)                             #顯示 Generation 平滑且黑色
    world.win.blit(text, (world.win_width-text.get_width() - 10, 50))

    world.bestNN.draw(world)

    py.display.update()
    world.win.blit(bg, (0,0))                    #將background放在畫面正中央

def main(genomes = [], config = []):
    global GEN
    GEN += 1                #迭代GEN

    nets = []
    ge = []
    cars = []
    t = 0

    world = World(STARTING_POS, WIN_WIDTH, WIN_HEIGHT)#world的construction function
    world.win.blit(bg, (0,0))       #將background放在畫面正中央

    NNs = []
    #這段看不太懂,應該是在從genomes加ge net NNs 
    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config) #創建一個對應gemoes 的net
        nets.append(net)         #將net放進nets vector中
        cars.append(Car(0, 0, 0))#把所有car都創建好
        g.fitness = 0
        ge.append(g)
        NNs.append(NN(config, g, (90, 210)))
    #
    road = Road(world)#Road的construction function
    clock = py.time.Clock() #開始計時

    run = True      #開始跑嘞
    while run:
        t += 1
        clock.tick(FPS)
        world.updateScore(0)#從0開始計時

        for event in py.event.get():    #迭代事件的迴圈，只要有事件發生就會處理
            if event.type == py.QUIT:   #如果使用者關視窗，程式結束
                run = False
                py.quit()
                quit()

        (xb, yb) = (0,0)        #將xbest與ybest設為0,0
        i = 0
        while(i < len(cars)):
            car = cars[i]

            input = car.getInputs(world, road)
            input.append(car.vel/MAX_VEL)
            car.commands = nets[i].activate(tuple(input))

            y_old = car.y       #紀錄car現在的位置
            (x, y) = car.move(road,t)   #移動car，將road和幀數當作parameter去計算car的移動

            if t>10 and (car.detectCollision(road) or y > world.getBestCarPos()[1] + BAD_GENOME_TRESHOLD or y>y_old or car.vel < 0.1): #t 用於避免在前幾幀消除機器（因為在前幾幀 getCollision() 總是返回 true）這段程式代表若car撞路了或car落後別人太多或太慢就移除
                ge[i].fitness -= 1
                cars.pop(i)
                nets.pop(i)
                ge.pop(i)
                NNs.pop(i)
            else:
                ge[i].fitness += -(y - y_old)/100 + car.vel*SCORE_VEL_MULTIPLIER #計算最後fitness
                if(ge[i].fitness > world.getScore()): #如果這次的fitness大於前面訓練的score
                    world.updateScore(ge[i].fitness)  #更新SCORE到這次的fitness
                    world.bestNN = NNs[i]             #更新最佳的NN
                    world.bestInputs = input          
                    world.bestCommands = car.commands
                i += 1

            if y < yb:  #紀錄有沒有超過best
                (xb, yb) = (x, y)


        if len(cars) == 0:#沒有車存活下來了
            run = False   #不跑了
            break

        world.updateBestCarPos((xb, yb))    #更新最佳pos
        road.update(world)                  #更新最佳路線
        draw_win(cars, road, world, GEN)    #


#NEAT function
def run(config_path):#用於加入config_file中的neat parameter
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)#將config_file中的參數加入config這個variable中

    p = neat.Population(config)#以下是計算在終端機上的那6個值

    p.add_reporter(neat.StdOutReporter(True))
    stats =neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 10000)

if __name__ == "__main__": #若開始跑main時
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_file.txt")
    run(config_path)   #加入config_file內的neat parameter
