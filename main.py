# main.py
import pygame
from simulation import Simulation # simulation.py의 Simulation 클래스 import
# import constants as const # Simulation 클래스가 내부적으로 constants를 사용하므로 main에서는 직접 필요 X

if __name__ == '__main__':
    pygame.init()       # Pygame 모듈 초기화
    pygame.font.init()  # Pygame 폰트 모듈 초기화 (Simulation 클래스에서 폰트 사용 시 안전장치)
    
    simulation_instance = Simulation()
    simulation_instance.run()
    
    pygame.quit()