# simulation.py
import pygame
import random
import math
import constants as const
from creatures import CreatureA, CreatureB, CreatureC

class Simulation:
    """시뮬레이션의 전체 상태와 핵심 로직을 관리하는 클래스입니다."""
    def __init__(self):
        # 전체 화면 크기로 Pygame 화면 초기화
        self.screen = pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
        pygame.display.set_caption("Ecosystem Simulation - Graph Right")
        self.clock = pygame.time.Clock()
        
        # 폰트 초기화 (HUD용, 그래프용)
        try:
            self.hud_font = pygame.font.Font(None, const.HUD_FONT_SIZE)
        except pygame.error:
            self.hud_font = pygame.font.SysFont("arial", const.HUD_FONT_SIZE)
        try:
            self.graph_font = pygame.font.Font(None, const.GRAPH_FONT_SIZE)
        except pygame.error:
            self.graph_font = pygame.font.SysFont("arial", const.GRAPH_FONT_SIZE)

        self.global_energy_pool = const.INITIAL_GLOBAL_ENERGY_POOL
        self.creatures_a, self.creatures_b, self.creatures_c = [], [], []
        self.species_luck = {'A': const.LUCK_DEFAULT, 'B': const.LUCK_DEFAULT, 'C': const.LUCK_DEFAULT}
        
        self.current_tick = 0
        self.last_simulation_update_time = pygame.time.get_ticks()
        self.is_running = False

        self.population_history = {'A': [], 'B': [], 'C': []}
        self.graph_mode = 'all'
        
        # 그래프 영역 정의 (화면 오른쪽)
        self.graph_surface_rect = pygame.Rect(
            const.GRAPH_AREA_X_START,
            const.GRAPH_PADDING, # 상단 패딩
            const.GRAPH_AREA_WIDTH,
            const.SCREEN_HEIGHT - (2 * const.GRAPH_PADDING) # 전체 높이에서 상하 패딩 제외
        )

        self._create_initial_creatures()

    def _get_random_position(self, radius):
        """시뮬레이션 영역 내 랜덤 좌표를 반환합니다."""
        x = random.uniform(radius, const.SIMULATION_AREA_WIDTH - radius)
        y = random.uniform(radius, const.SIMULATION_AREA_HEIGHT - radius)
        return x, y

    def _create_initial_creatures(self):
        for _ in range(const.CREATURE_A_INITIAL_COUNT):
            x, y = self._get_random_position(const.CREATURE_A_RADIUS)
            self.creatures_a.append(CreatureA(x, y, self.species_luck["A"]))
        for _ in range(const.CREATURE_B_INITIAL_COUNT):
            x, y = self._get_random_position(const.CREATURE_B_RADIUS)
            self.creatures_b.append(CreatureB(x, y, self.species_luck["B"]))
        for _ in range(const.CREATURE_C_INITIAL_COUNT):
            x, y = self._get_random_position(const.CREATURE_C_RADIUS)
            self.creatures_c.append(CreatureC(x, y, self.species_luck["C"]))

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0 or event.key == pygame.K_BACKQUOTE:
                    self.graph_mode = 'all'
                elif event.key == pygame.K_1:
                    self.graph_mode = 'A'
                elif event.key == pygame.K_2:
                    self.graph_mode = 'B'
                elif event.key == pygame.K_3:
                    self.graph_mode = 'C'

    def _spawn_creature_a(self):
        if self.current_tick > 0 and self.current_tick % const.CREATURE_A_CREATION_PERIOD_TICKS == 0:
            num_to_create_a = max(0, int(const.CREATURE_A_BASE_CREATION_COUNT * self.species_luck['A']))
            for _ in range(num_to_create_a):
                if self.global_energy_pool >= const.CREATURE_A_CREATION_COST:
                    self.global_energy_pool -= const.CREATURE_A_CREATION_COST
                    x, y = self._get_random_position(const.CREATURE_A_RADIUS)
                    new_a = CreatureA(x, y, self.species_luck['A'])
                    self.creatures_a.append(new_a)
                else:
                    break

    def _update_creatures_actions(self):
        newly_born_b = []
        for creature_b in self.creatures_b:
            if creature_b.is_alive:
                target_a = creature_b.find_target(self.creatures_a)
                creature_b.move(target_a)
                if target_a and target_a.is_alive:
                    creature_b.hunt(target_a) # hunt 내부에서 거리 체크
                if creature_b.can_reproduce():
                    offspring = creature_b.attempt_reproduction()
                    if offspring:
                        offspring.luck = self.species_luck["B"]
                        newly_born_b.append(offspring)
        self.creatures_b.extend(newly_born_b)

        newly_born_c = []
        for creature_c in self.creatures_c:
            if creature_c.is_alive:
                target_b = creature_c.find_target(self.creatures_b)
                creature_c.move(target_b)
                if target_b and target_b.is_alive:
                    creature_c.hunt(target_b) # hunt 내부에서 거리 체크
                if creature_c.can_reproduce():
                    offspring = creature_c.attempt_reproduction()
                    if offspring:
                        offspring.luck = self.species_luck["C"]
                        newly_born_c.append(offspring)
        self.creatures_c.extend(newly_born_c)

    def _update_creatures_age(self):
        for creature_list in [self.creatures_a, self.creatures_b, self.creatures_c]:
            for creature in creature_list:
                creature.update_age()

    def _process_deaths_and_energy_return(self):
        all_lists_map = {'A': self.creatures_a, 'B': self.creatures_b, 'C': self.creatures_c}
        new_lists_map = {'A': [], 'B': [], 'C': []}
        for species_key, creature_list in all_lists_map.items():
            for creature in creature_list:
                if creature.is_alive:
                    new_lists_map[species_key].append(creature)
                else:
                    if creature.age_ticks >= const.CREATURE_LIFESPAN_TICKS:
                        self.global_energy_pool += creature.current_energy_level
        self.creatures_a, self.creatures_b, self.creatures_c = new_lists_map['A'], new_lists_map['B'], new_lists_map['C']

    def _update_luck_system(self):
        if self.current_tick > 0 and self.current_tick % const.LUCK_ADJUSTMENT_PERIOD_TICKS == 0:
            num_a, num_b, num_c = len(self.creatures_a), len(self.creatures_b), len(self.creatures_c)
            total = num_a + num_b + num_c
            if total > 0:
                s_a,s_b,s_c = num_a/total, num_b/total, num_c/total
                self.species_luck['A'] = max(const.LUCK_MIN, min(const.LUCK_MAX, self.species_luck['A'] + (const.TARGET_RATIO_A_SHARE - s_a) * const.LUCK_ADJUSTMENT_K_FACTOR))
                self.species_luck['B'] = max(const.LUCK_MIN, min(const.LUCK_MAX, self.species_luck['B'] + (const.TARGET_RATIO_B_SHARE - s_b) * const.LUCK_ADJUSTMENT_K_FACTOR))
                self.species_luck['C'] = max(const.LUCK_MIN, min(const.LUCK_MAX, self.species_luck['C'] + (const.TARGET_RATIO_C_SHARE - s_c) * const.LUCK_ADJUSTMENT_K_FACTOR))
                for lst, luck_val in [(self.creatures_a,self.species_luck['A']),(self.creatures_b,self.species_luck['B']),(self.creatures_c,self.species_luck['C'])]:
                    for creature in lst: creature.luck = luck_val
            else: self.species_luck = {k: const.LUCK_DEFAULT for k in self.species_luck}

    def _update_population_history(self):
        self.population_history['A'].append(len(self.creatures_a))
        self.population_history['B'].append(len(self.creatures_b))
        self.population_history['C'].append(len(self.creatures_c))
        if const.GRAPH_MAX_HISTORY > 0:
            for key in self.population_history:
                while len(self.population_history[key]) > const.GRAPH_MAX_HISTORY:
                    self.population_history[key].pop(0)
    
    def _draw_population_graph(self):
        graph_rect = self.graph_surface_rect
        pygame.draw.rect(self.screen, const.GRAPH_BG_COLOR, graph_rect)
        pygame.draw.rect(self.screen, const.GRAPH_AXIS_COLOR, graph_rect, 1)

        species_map = {
            'A': (const.GRAPH_LINE_COLOR_A, self.population_history['A']),
            'B': (const.GRAPH_LINE_COLOR_B, self.population_history['B']),
            'C': (const.GRAPH_LINE_COLOR_C, self.population_history['C']),
        }
        active_keys = ['A', 'B', 'C'] if self.graph_mode == 'all' else ([self.graph_mode] if self.graph_mode in species_map else [])

        if not any(species_map[key][1] for key in active_keys): return

        max_pop_overall = 1
        current_max_history_len = 0
        for key in active_keys:
            history = species_map[key][1]
            if history:
                max_pop_overall = max(max_pop_overall, max(history))
                current_max_history_len = max(current_max_history_len, len(history))
        
        if current_max_history_len < 2: return

        # 내부 그래프 영역 (패딩 적용)
        inner_graph_x = graph_rect.left + const.GRAPH_PADDING * 3 # Y축 레이블 공간
        inner_graph_y = graph_rect.top + const.GRAPH_PADDING * 3  # X축 및 제목 공간
        inner_graph_width = graph_rect.width - const.GRAPH_PADDING * 4
        inner_graph_height = graph_rect.height - const.GRAPH_PADDING * 4


        # X축 그리기 (내부 그래프 영역 기준)
        pygame.draw.line(self.screen, const.GRAPH_AXIS_COLOR, 
                         (inner_graph_x, inner_graph_y + inner_graph_height), 
                         (inner_graph_x + inner_graph_width, inner_graph_y + inner_graph_height), 1)
        # Y축 그리기
        pygame.draw.line(self.screen, const.GRAPH_AXIS_COLOR,
                         (inner_graph_x, inner_graph_y),
                         (inner_graph_x, inner_graph_y + inner_graph_height), 1)


        for key in active_keys:
            line_color, history = species_map[key]
            if len(history) < 2: continue
            
            points = []
            num_points_to_draw = len(history) # 전체 히스토리 사용 (GRAPH_MAX_HISTORY는 이미 적용됨)
            point_spacing_x = inner_graph_width / (num_points_to_draw - 1) if num_points_to_draw > 1 else inner_graph_width

            for i, pop_count in enumerate(history):
                x = inner_graph_x + i * point_spacing_x
                y_val_norm = pop_count / max_pop_overall if max_pop_overall > 0 else 0
                y = inner_graph_y + inner_graph_height * (1 - y_val_norm) # Y축 반전
                points.append((x, y))
            
            if len(points) >= 2:
                pygame.draw.lines(self.screen, line_color, False, points, const.GRAPH_LINE_THICKNESS)

        # 레이블 및 제목
        title_text = f"Population Graph - Mode: {self.graph_mode.upper()}"
        title_surf = self.graph_font.render(title_text, True, const.GRAPH_TEXT_COLOR)
        self.screen.blit(title_surf, (graph_rect.centerx - title_surf.get_width() // 2, graph_rect.top + 5))

        max_pop_text = f"Max Pop: {max_pop_overall}"
        max_pop_surf = self.graph_font.render(max_pop_text, True, const.GRAPH_TEXT_COLOR)
        self.screen.blit(max_pop_surf, (inner_graph_x, graph_rect.top + const.GRAPH_PADDING + title_surf.get_height()))
        
        x_label_text = "Time (Ticks)"
        x_label_surf = self.graph_font.render(x_label_text, True, const.GRAPH_TEXT_COLOR)
        self.screen.blit(x_label_surf, (graph_rect.centerx - x_label_surf.get_width()//2, graph_rect.bottom - const.GRAPH_PADDING - x_label_surf.get_height()))

        y_label_text = "Count"
        y_label_surf = self.graph_font.render(y_label_text, True, const.GRAPH_TEXT_COLOR)
        y_label_surf = pygame.transform.rotate(y_label_surf, 90)
        self.screen.blit(y_label_surf, (graph_rect.left + 5, graph_rect.centery - y_label_surf.get_height()//2 ))


    def _draw_hud(self):
        hud_rect = const.HUD_AREA_RECT
        # pygame.draw.rect(self.screen, (10,10,10), hud_rect) # HUD 배경 (선택적)
        hud_info = [
            f"Tick: {self.current_tick}",
            f"Global Energy: {self.global_energy_pool:.2f}",
            f"A: {len(self.creatures_a)} (L: {self.species_luck['A']:.2f})",
            f"B: {len(self.creatures_b)} (L: {self.species_luck['B']:.2f})",
            f"C: {len(self.creatures_c)} (L: {self.species_luck['C']:.2f})"
        ]
        for i, line in enumerate(hud_info):
            text_surface = self.hud_font.render(line, True, const.GREY)
            # HUD_AREA_RECT 내부에 표시
            self.screen.blit(text_surface, (hud_rect.left + 5, hud_rect.top + 5 + i * (const.HUD_FONT_SIZE // 1.5)))


    def _render(self):
        self.screen.fill(const.BLACK) # 전체 화면 채우기

        # 시뮬레이션 영역 그리기 (개체들)
        # 개체들은 confine_to_screen에 의해 SIMULATION_AREA_WIDTH 내에 위치함
        for creature_list in [self.creatures_a, self.creatures_b, self.creatures_c]:
            for creature in creature_list:
                # 여기서 x좌표가 SIMULATION_AREA_WIDTH를 넘지 않는다고 가정
                creature.draw(self.screen) 
        
        self._draw_hud() # HUD 그리기 (시뮬레이션 영역 상단)
        self._draw_population_graph() # 그래프 그리기 (오른쪽 영역)

        pygame.display.flip()

    def run(self):
        self.is_running = True
        self.last_simulation_update_time = pygame.time.get_ticks()

        while self.is_running:
            self._handle_events()
            
            current_time_ms = pygame.time.get_ticks()
            if (current_time_ms - self.last_simulation_update_time) >= (const.SIMULATION_TICK_RATE * 1000):
                self.last_simulation_update_time = current_time_ms
                self.current_tick += 1

                self._spawn_creature_a()
                self._update_creatures_actions()
                self._update_creatures_age()
                self._process_deaths_and_energy_return()
                self._update_luck_system()
                self._update_population_history()
            
            self._render()
            self.clock.tick(const.FPS)