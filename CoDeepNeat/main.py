import pygame as py
import time
import os
import random
from car import Car
from road import Road
from world import World
from NNdraw import NN
from config_variables import *
import tfne

py.font.init()

bg = py.Surface((WIN_WIDTH, WIN_HEIGHT))
bg.fill(GRAY)

def draw_win(cars, road, world, GEN):
    road.draw(world)
    for car in cars:
        car.draw(world)

    text = STAT_FONT.render("Best Car Score: "+str(int(world.getScore())), 1, BLACK)
    world.win.blit(text, (world.win_width-text.get_width() - 10, 10))
    text = STAT_FONT.render("Gen: "+str(GEN), 1, BLACK)
    world.win.blit(text, (world.win_width-text.get_width() - 10, 50))

    world.bestNN.draw(world)

    py.display.update()
    world.win.blit(bg, (0,0))

class CarDrivingEnvironment(tfne.Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.world = World(STARTING_POS, WIN_WIDTH, WIN_HEIGHT)
        self.world.win.blit(bg, (0,0))
        self.road = Road(self.world)
        self.clock = py.time.Clock()

    def evaluate_genome(self, genome):
        car = Car(0, 0, 0)
        t = 0
        run = True

        # Initialize best car position
        xb, yb = 0, 0

        while run:
            t += 1
            self.clock.tick(FPS)
            self.world.updateScore(0)

            for event in py.event.get():
                if event.type == py.QUIT:
                    run = False
                    py.quit()
                    quit()

            input = car.getInputs(self.world, self.road)
            input.append(car.vel/MAX_VEL)
            car.commands = genome.activate(tuple(input)) # Using the genome to decide the commands

            y_old = car.y
            (x, y) = car.move(self.road,t)

            if t>10 and (car.detectCollision(self.road) or y > self.world.getBestCarPos()[1] + BAD_GENOME_TRESHOLD or y>y_old or car.vel < 0.1):
                return -(y - y_old)/100 + car.vel*SCORE_VEL_MULTIPLIER

            # If the car's y position is better than the best known, update the best known position
            if y < yb:
                xb, yb = x, y

            self.world.updateBestCarPos((xb, yb))
            self.road.update(self.world)
            draw_win([car], self.road, self.world, GEN)  # Pass [car] to draw_win as cars array


# CoDeepNEAT function
def run(config_path):
    config = tfne.parse_configuration(config_path)
    ne_algorithm = tfne.algorithms.CoDeepNEAT(config)

    environment = CarDrivingEnvironment(weight_training=True,
                                        config=config,
                                        verbosity=0)
    
    engine = tfne.EvolutionEngine(ne_algorithm=ne_algorithm,
                                 environment=environment,
                                 backup_dir_path='./',
                                 max_generations=64,
                                 max_fitness=100.0)

    best_genome = engine.train()

    print("Best genome returned by evolution:\n")
    print(best_genome)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_file.txt")
    run(config_path)
