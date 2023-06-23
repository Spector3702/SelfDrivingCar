import pygame as py

class Button:
    def __init__(self,x,y,image,scale):
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = py.transform.scale(image, (int(self.width*scale),int(self.height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False

    def draw(self,world):
        action = False
        pos = py.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if py.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if py.mouse.get_pressed()[0] == 0:
            self.clicked = False

        world.win.blit(self.image,self.rect.topleft)

        return action
        
    
        