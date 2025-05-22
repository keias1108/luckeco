# main.py
import pygame
from simulation import Simulation

if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    
    simulation_instance = Simulation()
    simulation_instance.run()
    
    pygame.quit()