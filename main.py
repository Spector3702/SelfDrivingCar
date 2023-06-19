import pygame as py
import neat
import time
import os
import random
import pickle
import glob
from car import Car
from road import Road
from world import World
from NNdraw import NN
from button import Button
from config_variables import *

py.font.init()

bg = py.Surface((WIN_WIDTH, WIN_HEIGHT)) # bg = background
bg.fill(BLACK) # 背景全黑

def draw_win(cars, road, world, GEN, BS, t):     #x 和 y 是最佳汽車的坐標
    global ROAD_DBG
    global CAR_DBG
    global PRE_TIME_C
    global PRE_TIME_R
    road.draw(world,ROAD_DBG)
    for car in cars:
        car.draw(world)
        
    text = STAT_FONT.render("Best Car Score: "+str(BS), 1, BRIGHT_GRAY)
    world.win.blit(text, (world.win_width-text.get_width() - 20, 20))
    
    text = STAT_FONT.render("Car Score: "+str(int(world.getScore())), 1, WHITE)
    world.win.blit(text, (world.win_width-text.get_width() - 20, 80))

    text = STAT_FONT.render("Gen: "+str(GEN), 1, WHITE)
    world.win.blit(text, (world.win_width-text.get_width() - 20, 140))

    text_road = STAT_FONT_2.render("Road Lines Visualization ", 1, GRAY)
    world.win.blit(text_road, (20, 560))

    #steering_wheel_img = py.transform.rotate(py.transform.scale(py.image.load(os.path.join('steering_wheel.png')).convert_alpha(),(SW_IMG_SIZE,SW_IMG_SIZE)),-BEST_CAR_ROTATION*3)

    #world.win.blit(steering_wheel_img,(SW_IMG_POS_X,SW_IMG_POS_Y))

    button_img = py.image.load(os.path.join("imgs",'botton.png')).convert_alpha()
    
    road_button = Button(25 + text_road.get_width(), 555, button_img, SCALE)

    road_clicked = False
    if road_button.draw(world) and not road_clicked:
        if (t - PRE_TIME_R) > 2:
            ROAD_DBG = not ROAD_DBG
            PRE_TIME_R = t
            road_clicked = True

    if not ROAD_DBG:
        text = STAT_FONT_2.render("ON", 1, GREEN_PALE)
        world.win.blit(text, (32 + text_road.get_width(), 560))
    else:
        text = STAT_FONT_2.render("OFF", 1, RED_PALE)
        world.win.blit(text, (30 + text_road.get_width(), 560))

    text_car = STAT_FONT_2.render("Car Sensor Visualization ", 1, GRAY)
    world.win.blit(text_car, (20, 590))

    car_button = Button(25 + text_car.get_width(), 585, button_img, SCALE)

    car_clicked = False
    if car_button.draw(world) and not car_clicked:
        if (t - PRE_TIME_C) > 2:
            CAR_DBG = not CAR_DBG
            PRE_TIME_C = t
            car_clicked = True

    if CAR_DBG:
        text = STAT_FONT_2.render("ON", 1, GREEN_PALE)
        world.win.blit(text, (32 + text_car.get_width(), 590))
    else:
        text = STAT_FONT_2.render("OFF", 1, RED_PALE)
        world.win.blit(text, (30 + text_car.get_width(), 590))

    text = STAT_FONT_2.render("Best Car Velocity = "+str(BEST_CAR_VEL), 1, GRAY)
    world.win.blit(text, (20, 620))
    
    text = STAT_FONT_2.render("Calculation Result = "+str(BEST_CAR_STATUS), 1, GRAY)
    world.win.blit(text, (20, 650))

    text = STAT_FONT_2.render("Best Car Rotation = "+str(BEST_CAR_ROTATION), 1, GRAY)
    world.win.blit(text, (20, 680))

    text = STAT_FONT_2.render("ROAD_WIDTH = "+str(ROAD_WIDTH), 1, GRAY)
    world.win.blit(text, (20, 710))

    text = STAT_FONT_1.render(str(len(cars))+' Car(s) Left', 1, GRAY)
    world.win.blit(text, (world.win_width-text.get_width() - 20, 710))

    ex_img = py.transform.rotate(py.transform.scale(py.image.load(os.path.join("imgs",'example_break.png')).convert_alpha(), (EX_IMG_SIZE_X,EX_IMG_SIZE_Y)), -90)
    world.win.blit(ex_img,(EX_IMG_POS_X, EX_IMG_SIZE_Y))

    world.bestNN.draw(world)

    py.display.update()
    world.win.blit(bg, (0,0))       #更新後立即 blit 背景所以如果我在 draw_win 之前繪製它們不會被背景覆蓋

def main(genomes = [], config = []):
    global GEN
    global BS
    global CAR_DBG
    global PRE_TIME_R
    global PRE_TIME_C
    global BEST_CAR_VEL
    global BEST_CAR_STATUS
    global BEST_CAR_ROTATION

    GEN += 1
    nets = []
    ge = []
    cars = []
    t = 0
    PRE_TIME_R = 0
    PRE_TIME_C = 0

    world = World(STARTING_POS, WIN_WIDTH, WIN_HEIGHT)
    world.win.blit(bg, (0,0))
    NNs = []

    if ISTEST:
        with open("best.pickle", "rb") as f:
            winner = pickle.load(f)
        net = neat.nn.FeedForwardNetwork.create(winner, config) #創建一個對應gemoes 的net
        nets.append(net)
        cars.append(Car(0, 0, 0))
        winner.fitness = 0
        ge.append(winner)
        NNs.append(NN(config, winner, (90, 210)))
    else:
        # 每個species有自己的genomes, 所以總共有population個genomes
        for _,g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config) #創建一個對應gemoes 的net
            nets.append(net)         #將net放進nets vector中
            cars.append(Car(0, 0, 0))#把所有car都創建好
            g.fitness = 0
            ge.append(g)
            NNs.append(NN(config, g, (90, 210)))

    road = Road(world)
    clock = py.time.Clock()

    run = True

    while run:
        t += 1
        clock.tick(FPS)
        world.saveScore(int(world.getScore()))
        BS = max(BS,int(world.getSave()))
        world.updateScore(0)
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
                py.quit()
                quit()
            if event.type == py.MOUSEBUTTONUP:
                pass

        (xb, yb) = (0,0)
        i = 0
        while(i < len(cars)):
            car = cars[i]

            input = car.getInputs(world, road,CAR_DBG)
            input.append(car.vel/MAX_VEL)
            car.commands = nets[i].activate(tuple(input))

            y_old = car.y
            (x, y) = car.move(road,t)

            if t>10 and (car.detectCollision(road) or y > world.getBestCarPos()[1] + BAD_GENOME_TRESHOLD or y>y_old or car.vel < 0.1): #il t serve a evitare di eliminare macchine nei primi tot frame (nei primi frame getCollision() restituisce sempre true)
                ge[i].fitness -= 1
                cars.pop(i)
                nets.pop(i)
                ge.pop(i)
                NNs.pop(i)
            else:
                ge[i].fitness += -(y - y_old)/100 + car.vel*SCORE_VEL_MULTIPLIER
                if(ge[i].fitness > world.getScore()):
                    world.updateScore(ge[i].fitness)
                    world.bestNN = NNs[i]
                    world.bestInputs = input
                    world.bestCommands = car.commands                    
                    BEST_CAR_VEL = round(car.vel, 5)
                    command_list = [0,0,0,0]
                    for command in range(4):
                        command_list[command] = round(car.commands[command],7)
                    BEST_CAR_STATUS = command_list
                    BEST_CAR_ROTATION = car.rot
                i += 1

            if y < yb:
                (xb, yb) = (x, y)

        
        if len(cars) == 0:
            run = False
            break
        
        world.updateBestCarPos((xb, yb))
        road.update(world)
        draw_win(cars, road, world, GEN + last_gen, BS, t)
 

#NEAT function
def run(config_path):
    checkpoint_path = './checkpoints/neat-checkpoint-'
    global last_gen

    # if run first time
    if (len(glob.glob(checkpoint_path + '*')) == 0  or ISTEST):
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)#將config_file中的參數加入config這個variable中
        p = neat.Population(config)
        last_gen = 0
    # if continue training
    else:
        gen_num = []
        for file in glob.glob(checkpoint_path + '*'):
            gen_num.append(int(file[len(checkpoint_path):]))
        p = neat.Checkpointer.restore_checkpoint(checkpoint_path + str(max(gen_num)))
        last_gen = p.generation

    p.add_reporter(neat.StdOutReporter(True))
    stats =neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(GEN_INTERVAL, filename_prefix = checkpoint_path))
    winner = p.run(main, MAX_GEN) # Runs NEAT’s genetic algorithm for at most n generations. n : The maximum number of generations to run
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_file.txt")
    run(config_path)
