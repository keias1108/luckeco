# creatures.py
import pygame
import random
import math
import uuid
import constants as const

# --- 헬퍼 함수 ---
def calculate_distance_objects(obj1, obj2):
    """두 개체 객체 사이의 거리를 계산합니다."""
    if not obj1 or not obj2:
        return float('inf')
    return math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)

class Creature:
    """생태계 내 모든 개체의 기본 클래스입니다."""
    def __init__(self, x, y, radius, color, species_name, initial_luck, fixed_energy_value):
        self.id = uuid.uuid4()
        self.x = float(x) # x 좌표는 Simulation._get_random_position에서 시뮬레이션 영역 내로 주어짐
        self.y = float(y) # y 좌표는 Simulation._get_random_position에서 시뮬레이션 영역 내로 주어짐
        self.radius = int(radius)
        self.color = color
        self.luck = float(initial_luck)
        self.age_ticks = 0
        self.is_alive = True
        self.species_name = species_name
        self.fixed_energy_value = float(fixed_energy_value)
        self.current_energy_level = float(fixed_energy_value)
        self.confine_to_screen() # 초기 위치 보정

    def draw(self, screen):
        if self.is_alive:
            # 시뮬레이션 영역 내에서만 그려지도록 보장 (Simulation 클래스의 _render에서 처리)
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
        """개체가 시뮬레이션 영역 경계를 벗어나지 않도록 위치를 조정합니다."""
        self.x = max(self.radius, min(self.x, const.SIMULATION_AREA_WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, const.SIMULATION_AREA_HEIGHT - self.radius))

    def __repr__(self):
        return (f"{self.species_name}(id={str(self.id)[:8]}, age={self.age_ticks}, "
                f"luck={self.luck:.2f}, E:{self.current_energy_level:.2f})")

class CreatureA(Creature):
    """A 종 개체 클래스입니다."""
    def __init__(self, x, y, initial_luck):
        super().__init__(x, y, const.CREATURE_A_RADIUS, const.GREEN, "A",
                         initial_luck, const.CREATURE_A_FIXED_ENERGY)

class CreatureB(Creature):
    """B 종 개체 클래스입니다. A를 사냥합니다."""
    base_speed = const.CREATURE_B_BASE_MOVE_SPEED

    def __init__(self, x, y, initial_luck):
        super().__init__(x, y, const.CREATURE_B_RADIUS, const.BLUE, "B",
                         initial_luck, const.CREATURE_B_FIXED_ENERGY)
        self.eaten_prey_count = 0

    def get_current_speed(self):
        return self.base_speed * self.luck

    def find_target(self, creatures_a_list):
        closest_target = None
        min_dist_sq = const.CREATURE_B_HUNT_RADIUS ** 2
        for target_a in creatures_a_list:
            if target_a.is_alive:
                dist_sq = (self.x - target_a.x)**2 + (self.y - target_a.y)**2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_target = target_a
        return closest_target

    def move(self, target_a):
        if not self.is_alive: return
        current_speed = self.get_current_speed()
        if current_speed <= 0: return

        if target_a and target_a.is_alive:
            angle = math.atan2(target_a.y - self.y, target_a.x - self.x)
            self.x += math.cos(angle) * current_speed
            self.y += math.sin(angle) * current_speed
        else:
            self.move_randomly(current_speed)
        self.confine_to_screen()

    def hunt(self, target_a):
        if not self.is_alive or not target_a or not target_a.is_alive: return False
        
        distance = calculate_distance_objects(self, target_a) # 거리 체크는 hunt 메서드 내에 유지
        if distance <= (self.radius + target_a.radius):
            target_a.is_alive = False
            self.eaten_prey_count += 1
            self.current_energy_level += target_a.fixed_energy_value
            return True
        return False

    def can_reproduce(self):
        return self.eaten_prey_count >= const.CREATURE_B_PREY_COUNT_FOR_REPRODUCTION

    def attempt_reproduction(self):
        if random.random() < (const.CREATURE_B_BASE_REPRODUCTION_SUCCESS_RATE * self.luck):
            self.eaten_prey_count = 0
            spawn_x = self.x + random.uniform(-self.radius*2, self.radius*2)
            spawn_y = self.y + random.uniform(-self.radius*2, self.radius*2)
            return CreatureB(spawn_x, spawn_y, self.luck)
        return None

class CreatureC(Creature):
    """C 종 개체 클래스입니다. B를 사냥합니다."""
    base_speed = const.CREATURE_C_BASE_MOVE_SPEED

    def __init__(self, x, y, initial_luck):
        super().__init__(x, y, const.CREATURE_C_RADIUS, const.RED, "C",
                         initial_luck, const.CREATURE_C_FIXED_ENERGY)
        self.eaten_prey_count = 0

    def get_current_speed(self):
        return self.base_speed * self.luck

    def find_target(self, creatures_b_list):
        closest_target = None
        min_dist_sq = const.CREATURE_C_HUNT_RADIUS ** 2
        for target_b in creatures_b_list:
            if target_b.is_alive:
                dist_sq = (self.x - target_b.x)**2 + (self.y - target_b.y)**2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_target = target_b
        return closest_target

    def move(self, target_b):
        if not self.is_alive: return
        current_speed = self.get_current_speed()
        if current_speed <= 0: return

        if target_b and target_b.is_alive:
            angle = math.atan2(target_b.y - self.y, target_b.x - self.x)
            self.x += math.cos(angle) * current_speed
            self.y += math.sin(angle) * current_speed
        else:
            self.move_randomly(current_speed)
        self.confine_to_screen()
        
    def hunt(self, target_b):
        if not self.is_alive or not target_b or not target_b.is_alive: return False

        distance = calculate_distance_objects(self, target_b) # 거리 체크는 hunt 메서드 내에 유지
        if distance <= (self.radius + target_b.radius):
            target_b.is_alive = False
            self.eaten_prey_count += 1
            self.current_energy_level += target_b.fixed_energy_value
            return True
        return False

    def can_reproduce(self):
        return self.eaten_prey_count >= const.CREATURE_C_PREY_COUNT_FOR_REPRODUCTION

    def attempt_reproduction(self):
        if random.random() < (const.CREATURE_C_BASE_REPRODUCTION_SUCCESS_RATE * self.luck):
            self.eaten_prey_count = 0
            spawn_x = self.x + random.uniform(-self.radius*2, self.radius*2)
            spawn_y = self.y + random.uniform(-self.radius*2, self.radius*2)
            return CreatureC(spawn_x, spawn_y, self.luck)
        return None