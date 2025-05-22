# creatures.py
import pygame
import random
import math
import uuid
import constants as const

# --- 헬퍼 함수 ---
def calculate_distance_objects(obj1, obj2):
    if not obj1 or not obj2: return float('inf')
    return math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)

class Creature:
    def __init__(self, x, y, radius, color, species_name, initial_luck, fixed_energy_value):
        self.id = uuid.uuid4()
        self.x = float(x)
        self.y = float(y)
        self.radius = int(radius)
        self.color = color
        self.luck = float(initial_luck)
        self.age_ticks = 0
        self.is_alive = True
        self.species_name = species_name
        self.fixed_energy_value = float(fixed_energy_value)
        self.current_energy_level = float(fixed_energy_value)
        self.eaten_prey_count = 0 # 모든 포식자가 가질 수 있도록 Creature 클래스로 이동
        self.confine_to_screen()

    def draw(self, screen):
        if self.is_alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update_age(self):
        if self.is_alive:
            self.age_ticks += 1
            if self.age_ticks >= const.CREATURE_LIFESPAN_TICKS:
                self.is_alive = False

    def move_randomly(self, speed):
        if self.is_alive and speed > 0:
            angle = random.uniform(0, 2 * math.pi)
            self.x += math.cos(angle) * speed
            self.y += math.sin(angle) * speed
            self.confine_to_screen()

    def confine_to_screen(self):
        self.x = max(self.radius, min(self.x, const.SIMULATION_AREA_WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, const.SIMULATION_AREA_HEIGHT - self.radius))

    def get_current_speed(self): # 기본 구현, 하위 클래스에서 오버라이드 가능
        if hasattr(self, 'base_speed'):
            return self.base_speed * self.luck
        return 1.0 * self.luck # base_speed가 없는 경우 (예: CreatureA)

    def _base_hunt_logic(self, target): # 포식자 클래스에서 사용할 공통 로직
        if not self.is_alive or not target or not target.is_alive: return False
        if calculate_distance_objects(self,target) <= (self.radius+target.radius):
            target.is_alive=False
            self.eaten_prey_count+=1
            self.current_energy_level+=target.fixed_energy_value
            return True
        return False

    def __repr__(self):
        return (f"{self.species_name}(id={str(self.id)[:8]}, age={self.age_ticks}, "
                f"luck={self.luck:.2f}, E:{self.current_energy_level:.2f})")

class CreatureA(Creature):
    def __init__(self, x, y, initial_luck):
        super().__init__(x, y, const.CREATURE_A_RADIUS, const.GREEN, "A",
                         initial_luck, const.CREATURE_A_FIXED_ENERGY)
    # A는 사냥하거나 특정 방식으로 번식하지 않음 (Simulation 클래스에서 생성)

class CreatureB(Creature):
    base_speed = const.CREATURE_B_BASE_MOVE_SPEED
    def __init__(self, x, y, initial_luck):
        super().__init__(x, y, const.CREATURE_B_RADIUS, const.BLUE, "B",
                         initial_luck, const.CREATURE_B_FIXED_ENERGY)
    def find_target(self, creatures_a_list):
        closest = None; min_d_sq = const.CREATURE_B_HUNT_RADIUS**2
        for t in creatures_a_list:
            if t.is_alive:
                d_sq=(self.x-t.x)**2+(self.y-t.y)**2
                if d_sq<min_d_sq: min_d_sq=d_sq; closest=t
        return closest
    def move(self, target):
        if not self.is_alive: return
        s=self.get_current_speed()
        if s<=0:return
        if target and target.is_alive:
            a=math.atan2(target.y-self.y,target.x-self.x); self.x+=s*math.cos(a); self.y+=s*math.sin(a)
        else: self.move_randomly(s)
        self.confine_to_screen()
    def hunt(self, target_a): return self._base_hunt_logic(target_a)
    def can_reproduce(self): return self.eaten_prey_count >= const.CREATURE_B_PREY_COUNT_FOR_REPRODUCTION
    def attempt_reproduction(self):
        if random.random()<(const.CREATURE_B_BASE_REPRODUCTION_SUCCESS_RATE*self.luck):
            self.eaten_prey_count=0; sx=self.x+random.uniform(-self.radius*2,self.radius*2); sy=self.y+random.uniform(-self.radius*2,self.radius*2)
            return CreatureB(sx,sy,self.luck)
        return None

class CreatureC(Creature):
    base_speed = const.CREATURE_C_BASE_MOVE_SPEED
    def __init__(self, x, y, initial_luck):
        super().__init__(x, y, const.CREATURE_C_RADIUS, const.RED, "C",
                         initial_luck, const.CREATURE_C_FIXED_ENERGY)
    def find_target(self, creatures_b_list): # Hunts B
        closest=None; min_d_sq=const.CREATURE_C_HUNT_RADIUS**2
        for t in creatures_b_list:
            if t.is_alive:
                d_sq=(self.x-t.x)**2+(self.y-t.y)**2
                if d_sq<min_d_sq: min_d_sq=d_sq; closest=t
        return closest
    def move(self, target):
        if not self.is_alive: return
        s=self.get_current_speed()
        if s<=0:return
        if target and target.is_alive:
            a=math.atan2(target.y-self.y,target.x-self.x); self.x+=s*math.cos(a); self.y+=s*math.sin(a)
        else: self.move_randomly(s)
        self.confine_to_screen()
    def hunt(self, target_b): return self._base_hunt_logic(target_b) # Hunts B
    def can_reproduce(self): return self.eaten_prey_count >= const.CREATURE_C_PREY_COUNT_FOR_REPRODUCTION
    def attempt_reproduction(self):
        if random.random()<(const.CREATURE_C_BASE_REPRODUCTION_SUCCESS_RATE*self.luck):
            self.eaten_prey_count=0; sx=self.x+random.uniform(-self.radius*2,self.radius*2); sy=self.y+random.uniform(-self.radius*2,self.radius*2)
            return CreatureC(sx,sy,self.luck)
        return None

# --- New Fixed Species ---
class CreatureD(Creature):
    base_speed = const.CREATURE_D_BASE_MOVE_SPEED
    def __init__(self, x, y, initial_luck):
        super().__init__(x,y,const.CREATURE_D_RADIUS, const.YELLOW, "D", initial_luck, const.CREATURE_D_FIXED_ENERGY)
    def find_target(self, creatures_c_list): # Hunts C
        closest=None; min_d_sq=const.CREATURE_D_HUNT_RADIUS**2
        for t in creatures_c_list:
            if t.is_alive:
                d_sq=(self.x-t.x)**2+(self.y-t.y)**2
                if d_sq<min_d_sq: min_d_sq=d_sq; closest=t
        return closest
    def move(self,target): # Copied from C, target is C
        if not self.is_alive:return
        s=self.get_current_speed()
        if s<=0:return
        if target and target.is_alive:
            a=math.atan2(target.y-self.y,target.x-self.x); self.x+=s*math.cos(a); self.y+=s*math.sin(a)
        else: self.move_randomly(s)
        self.confine_to_screen()
    def hunt(self, target_c): return self._base_hunt_logic(target_c)
    def can_reproduce(self): return self.eaten_prey_count >= const.CREATURE_D_PREY_COUNT_FOR_REPRODUCTION
    def attempt_reproduction(self):
        if random.random()<(const.CREATURE_D_BASE_REPRODUCTION_SUCCESS_RATE*self.luck):
            self.eaten_prey_count=0; sx=self.x+random.uniform(-self.radius*2,self.radius*2); sy=self.y+random.uniform(-self.radius*2,self.radius*2)
            return CreatureD(sx,sy,self.luck)
        return None

class CreatureE(Creature):
    base_speed = const.CREATURE_E_BASE_MOVE_SPEED
    def __init__(self, x, y, initial_luck):
        super().__init__(x,y,const.CREATURE_E_RADIUS, const.CYAN, "E", initial_luck, const.CREATURE_E_FIXED_ENERGY)
    def find_target(self, creatures_d_list): # Hunts D
        closest=None; min_d_sq=const.CREATURE_E_HUNT_RADIUS**2
        for t in creatures_d_list:
            if t.is_alive:
                d_sq=(self.x-t.x)**2+(self.y-t.y)**2
                if d_sq<min_d_sq: min_d_sq=d_sq; closest=t
        return closest
    def move(self,target): # Target is D
        if not self.is_alive:return
        s=self.get_current_speed()
        if s<=0:return
        if target and target.is_alive:
            a=math.atan2(target.y-self.y,target.x-self.x); self.x+=s*math.cos(a); self.y+=s*math.sin(a)
        else: self.move_randomly(s)
        self.confine_to_screen()
    def hunt(self, target_d): return self._base_hunt_logic(target_d)
    def can_reproduce(self): return self.eaten_prey_count >= const.CREATURE_E_PREY_COUNT_FOR_REPRODUCTION
    def attempt_reproduction(self):
        if random.random()<(const.CREATURE_E_BASE_REPRODUCTION_SUCCESS_RATE*self.luck):
            self.eaten_prey_count=0; sx=self.x+random.uniform(-self.radius*2,self.radius*2); sy=self.y+random.uniform(-self.radius*2,self.radius*2)
            return CreatureE(sx,sy,self.luck)
        return None

class CreatureF(Creature):
    base_speed = const.CREATURE_F_BASE_MOVE_SPEED
    def __init__(self, x, y, initial_luck):
        super().__init__(x,y,const.CREATURE_F_RADIUS, const.MAGENTA, "F", initial_luck, const.CREATURE_F_FIXED_ENERGY)
    def find_target(self, creatures_e_list): # Hunts E
        closest=None; min_d_sq=const.CREATURE_F_HUNT_RADIUS**2
        for t in creatures_e_list:
            if t.is_alive:
                d_sq=(self.x-t.x)**2+(self.y-t.y)**2
                if d_sq<min_d_sq: min_d_sq=d_sq; closest=t
        return closest
    def move(self,target):# Target is E
        if not self.is_alive:return
        s=self.get_current_speed()
        if s<=0:return
        if target and target.is_alive:
            a=math.atan2(target.y-self.y,target.x-self.x); self.x+=s*math.cos(a); self.y+=s*math.sin(a)
        else: self.move_randomly(s)
        self.confine_to_screen()
    def hunt(self, target_e): return self._base_hunt_logic(target_e)
    def can_reproduce(self): return self.eaten_prey_count >= const.CREATURE_F_PREY_COUNT_FOR_REPRODUCTION
    def attempt_reproduction(self):
        if random.random()<(const.CREATURE_F_BASE_REPRODUCTION_SUCCESS_RATE*self.luck):
            self.eaten_prey_count=0; sx=self.x+random.uniform(-self.radius*2,self.radius*2); sy=self.y+random.uniform(-self.radius*2,self.radius*2)
            return CreatureF(sx,sy,self.luck)
        return None

class CreatureG(Creature):
    base_speed = const.CREATURE_G_BASE_MOVE_SPEED
    def __init__(self, x, y, initial_luck):
        super().__init__(x,y,const.CREATURE_G_RADIUS, const.ORANGE, "G", initial_luck, const.CREATURE_G_FIXED_ENERGY)
    def find_target(self, creatures_f_list): # Hunts F
        closest=None; min_d_sq=const.CREATURE_G_HUNT_RADIUS**2
        for t in creatures_f_list:
            if t.is_alive:
                d_sq=(self.x-t.x)**2+(self.y-t.y)**2
                if d_sq<min_d_sq: min_d_sq=d_sq; closest=t
        return closest
    def move(self,target):# Target is F
        if not self.is_alive:return
        s=self.get_current_speed()
        if s<=0:return
        if target and target.is_alive:
            a=math.atan2(target.y-self.y,target.x-self.x); self.x+=s*math.cos(a); self.y+=s*math.sin(a)
        else: self.move_randomly(s)
        self.confine_to_screen()
    def hunt(self, target_f): return self._base_hunt_logic(target_f)
    def can_reproduce(self): return self.eaten_prey_count >= const.CREATURE_G_PREY_COUNT_FOR_REPRODUCTION
    def attempt_reproduction(self):
        if random.random()<(const.CREATURE_G_BASE_REPRODUCTION_SUCCESS_RATE*self.luck):
            self.eaten_prey_count=0; sx=self.x+random.uniform(-self.radius*2,self.radius*2); sy=self.y+random.uniform(-self.radius*2,self.radius*2)
            return CreatureG(sx,sy,self.luck)
        return None

class CreatureH(Creature):
    base_speed = const.CREATURE_H_BASE_MOVE_SPEED
    def __init__(self, x, y, initial_luck):
        super().__init__(x,y,const.CREATURE_H_RADIUS, const.PURPLE, "H", initial_luck, const.CREATURE_H_FIXED_ENERGY)
    def find_target(self, creatures_g_list): # Hunts G
        closest=None; min_d_sq=const.CREATURE_H_HUNT_RADIUS**2
        for t in creatures_g_list:
            if t.is_alive:
                d_sq=(self.x-t.x)**2+(self.y-t.y)**2
                if d_sq<min_d_sq: min_d_sq=d_sq; closest=t
        return closest
    def move(self,target):# Target is G
        if not self.is_alive:return
        s=self.get_current_speed()
        if s<=0:return
        if target and target.is_alive:
            a=math.atan2(target.y-self.y,target.x-self.x); self.x+=s*math.cos(a); self.y+=s*math.sin(a)
        else: self.move_randomly(s)
        self.confine_to_screen()
    def hunt(self, target_g): return self._base_hunt_logic(target_g)
    def can_reproduce(self): return self.eaten_prey_count >= const.CREATURE_H_PREY_COUNT_FOR_REPRODUCTION
    def attempt_reproduction(self):
        if random.random()<(const.CREATURE_H_BASE_REPRODUCTION_SUCCESS_RATE*self.luck):
            self.eaten_prey_count=0; sx=self.x+random.uniform(-self.radius*2,self.radius*2); sy=self.y+random.uniform(-self.radius*2,self.radius*2)
            return CreatureH(sx,sy,self.luck)
        return None

class CreatureI(Creature):
    base_speed = const.CREATURE_I_BASE_MOVE_SPEED
    def __init__(self, x, y, initial_luck):
        super().__init__(x,y,const.CREATURE_I_RADIUS, const.BROWN, "I", initial_luck, const.CREATURE_I_FIXED_ENERGY)
    def find_target(self, creatures_h_list): # Hunts H
        closest=None; min_d_sq=const.CREATURE_I_HUNT_RADIUS**2
        for t in creatures_h_list:
            if t.is_alive:
                d_sq=(self.x-t.x)**2+(self.y-t.y)**2
                if d_sq<min_d_sq: min_d_sq=d_sq; closest=t
        return closest
    def move(self,target):# Target is H
        if not self.is_alive:return
        s=self.get_current_speed()
        if s<=0:return
        if target and target.is_alive:
            a=math.atan2(target.y-self.y,target.x-self.x); self.x+=s*math.cos(a); self.y+=s*math.sin(a)
        else: self.move_randomly(s)
        self.confine_to_screen()
    def hunt(self, target_h): return self._base_hunt_logic(target_h)
    def can_reproduce(self): return self.eaten_prey_count >= const.CREATURE_I_PREY_COUNT_FOR_REPRODUCTION
    def attempt_reproduction(self):
        if random.random()<(const.CREATURE_I_BASE_REPRODUCTION_SUCCESS_RATE*self.luck):
            self.eaten_prey_count=0; sx=self.x+random.uniform(-self.radius*2,self.radius*2); sy=self.y+random.uniform(-self.radius*2,self.radius*2)
            return CreatureI(sx,sy,self.luck)
        return None