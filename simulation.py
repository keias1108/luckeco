# simulation.py
import pygame
import random
import math
import os # For graph saving path
import constants as const
from creatures import CreatureA, CreatureB, CreatureC

class Simulation:
    """시뮬레이션의 전체 상태와 핵심 로직을 관리하는 클래스입니다."""
    def __init__(self):
        self.screen = pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
        pygame.display.set_caption("Ecosystem Simulation - Controls & Graph Save")
        self.clock = pygame.time.Clock()
        
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
        self.graph_surface_rect = pygame.Rect(
            const.GRAPH_AREA_X_START, const.GRAPH_PADDING,
            const.GRAPH_AREA_WIDTH, const.SCREEN_HEIGHT - (2 * const.GRAPH_PADDING)
        )

        # 시뮬레이션 제어 상태 변수 추가
        self.is_paused = False
        self.simulation_speed_factor_index = 0 # FAST_FORWARD_FACTORS 리스트의 인덱스
        self.simulation_speed_factor = const.FAST_FORWARD_FACTORS[self.simulation_speed_factor_index]

        self._create_initial_creatures()

    def _get_random_position(self, radius):
        x = random.uniform(radius, const.SIMULATION_AREA_WIDTH - radius)
        y = random.uniform(radius, const.SIMULATION_AREA_HEIGHT - radius)
        return x, y

    def _create_initial_creatures(self):
        # 내용은 기존과 동일 (Simulation Area 내 생성)
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
                # 그래프 모드 변경 (기존 로직 유지)
                if event.key == pygame.K_0 or event.key == pygame.K_BACKQUOTE:
                    self.graph_mode = 'all'
                elif event.key == pygame.K_1: self.graph_mode = 'A'
                elif event.key == pygame.K_2: self.graph_mode = 'B'
                elif event.key == pygame.K_3: self.graph_mode = 'C'
                
                # 시뮬레이션 제어 키 입력 처리
                elif event.key == pygame.K_SPACE: # 정지/시작 토글
                    self.is_paused = not self.is_paused
                elif event.key == pygame.K_RIGHT: # 앞으로 감기 속도 변경
                    self.simulation_speed_factor_index = (self.simulation_speed_factor_index + 1) % len(const.FAST_FORWARD_FACTORS)
                    self.simulation_speed_factor = const.FAST_FORWARD_FACTORS[self.simulation_speed_factor_index]
                elif event.key == pygame.K_s: # 그래프 저장
                    self._save_graph_as_image()


    def _spawn_creature_a(self): # 기존 로직 유지
        if self.current_tick > 0 and self.current_tick % const.CREATURE_A_CREATION_PERIOD_TICKS == 0:
            num_to_create_a = max(0, int(const.CREATURE_A_BASE_CREATION_COUNT * self.species_luck['A']))
            for _ in range(num_to_create_a):
                if self.global_energy_pool >= const.CREATURE_A_CREATION_COST:
                    self.global_energy_pool -= const.CREATURE_A_CREATION_COST
                    x, y = self._get_random_position(const.CREATURE_A_RADIUS)
                    new_a = CreatureA(x, y, self.species_luck['A'])
                    self.creatures_a.append(new_a)
                else: break

    def _update_creatures_actions(self): # 기존 로직 유지
        newly_born_b = []
        for creature_b in self.creatures_b:
            if creature_b.is_alive:
                target_a = creature_b.find_target(self.creatures_a)
                creature_b.move(target_a)
                if target_a and target_a.is_alive: creature_b.hunt(target_a)
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
                if target_b and target_b.is_alive: creature_c.hunt(target_b)
                if creature_c.can_reproduce():
                    offspring = creature_c.attempt_reproduction()
                    if offspring:
                        offspring.luck = self.species_luck["C"]
                        newly_born_c.append(offspring)
        self.creatures_c.extend(newly_born_c)

    def _update_creatures_age(self): # 기존 로직 유지
        for creature_list in [self.creatures_a, self.creatures_b, self.creatures_c]:
            for creature in creature_list: creature.update_age()

    def _process_deaths_and_energy_return(self): # 기존 에너지 수정 로직 유지
        all_lists_map = {'A': self.creatures_a, 'B': self.creatures_b, 'C': self.creatures_c}
        new_lists_map = {'A': [], 'B': [], 'C': []}
        for species_key, creature_list in all_lists_map.items():
            for creature in creature_list:
                if creature.is_alive: new_lists_map[species_key].append(creature)
                else:
                    if creature.age_ticks >= const.CREATURE_LIFESPAN_TICKS:
                        self.global_energy_pool += creature.current_energy_level
        self.creatures_a, self.creatures_b, self.creatures_c = new_lists_map['A'], new_lists_map['B'], new_lists_map['C']

    def _update_luck_system(self): # 기존 로직 유지
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

    def _update_population_history(self): # 기존 로직 유지
        self.population_history['A'].append(len(self.creatures_a))
        self.population_history['B'].append(len(self.creatures_b))
        self.population_history['C'].append(len(self.creatures_c))
        if const.GRAPH_MAX_HISTORY > 0:
            for key in self.population_history:
                while len(self.population_history[key]) > const.GRAPH_MAX_HISTORY:
                    self.population_history[key].pop(0)
    
    def _draw_population_graph(self, target_surface=None, history_data=None, graph_rect_override=None, full_history_mode=False):
        """개체 수 변화 그래프를 그립니다. 화면 또는 별도 Surface에 그릴 수 있습니다."""
        surface_to_draw_on = target_surface if target_surface else self.screen
        current_history = history_data if history_data else self.population_history
        graph_rect = graph_rect_override if graph_rect_override else self.graph_surface_rect

        pygame.draw.rect(surface_to_draw_on, const.GRAPH_BG_COLOR, graph_rect)
        pygame.draw.rect(surface_to_draw_on, const.GRAPH_AXIS_COLOR, graph_rect, 1)

        species_map = {
            'A': (const.GRAPH_LINE_COLOR_A, current_history['A']),
            'B': (const.GRAPH_LINE_COLOR_B, current_history['B']),
            'C': (const.GRAPH_LINE_COLOR_C, current_history['C']),
        }
        active_keys = ['A', 'B', 'C'] if self.graph_mode == 'all' or full_history_mode else ([self.graph_mode] if self.graph_mode in species_map else [])

        if not any(species_map[key][1] for key in active_keys if key in species_map and species_map[key]): return

        max_pop_overall = 1
        max_history_len_for_scale = 0 # X축 스케일링 기준이 될 최대 길이

        for key in active_keys:
            if key not in species_map: continue
            history = species_map[key][1]
            if history:
                max_pop_overall = max(max_pop_overall, max(history))
                max_history_len_for_scale = max(max_history_len_for_scale, len(history))
        
        if max_history_len_for_scale < 2 and not full_history_mode: return # 화면 표시는 최소 2개 점 필요
        if full_history_mode and max_history_len_for_scale == 0 : return # 저장시에도 데이터 없으면 종료


        # 내부 그래프 영역 (패딩 및 레이블 공간 고려)
        # Y축 레이블 회전 시 필요한 너비가 적으므로 패딩을 좀 더 확보
        y_axis_label_space = const.GRAPH_PADDING * 2 + self.graph_font.get_height() if full_history_mode else const.GRAPH_PADDING * 3
        x_axis_label_space = const.GRAPH_PADDING * 2 + self.graph_font.get_height()

        inner_graph_x = graph_rect.left + y_axis_label_space
        inner_graph_y = graph_rect.top + const.GRAPH_PADDING * 2 # 제목 및 Max Pop 표시 공간
        inner_graph_width = graph_rect.width - y_axis_label_space - const.GRAPH_PADDING
        inner_graph_height = graph_rect.height - (const.GRAPH_PADDING * 3) - x_axis_label_space # 제목, X축 레이블 공간

        if inner_graph_width <=0 or inner_graph_height <=0: return # 그릴 공간 없음

        # X축, Y축 그리기
        pygame.draw.line(surface_to_draw_on, const.GRAPH_AXIS_COLOR, (inner_graph_x, inner_graph_y + inner_graph_height), (inner_graph_x + inner_graph_width, inner_graph_y + inner_graph_height), 1)
        pygame.draw.line(surface_to_draw_on, const.GRAPH_AXIS_COLOR, (inner_graph_x, inner_graph_y), (inner_graph_x, inner_graph_y + inner_graph_height), 1)

        for key in active_keys:
            if key not in species_map: continue
            line_color, history = species_map[key]
            
            # 화면 표시는 GRAPH_MAX_HISTORY 제한, 전체 저장은 전체 히스토리
            data_to_plot = history
            if not full_history_mode and const.GRAPH_MAX_HISTORY > 0 and len(history) > const.GRAPH_MAX_HISTORY:
                data_to_plot = history[-const.GRAPH_MAX_HISTORY:]
            
            num_points_to_draw = len(data_to_plot)
            if num_points_to_draw < (1 if full_history_mode and num_points_to_draw == 1 else 2) : continue # 점 하나는 그릴 수 있음 (저장시)

            point_spacing_x = inner_graph_width / (num_points_to_draw - 1) if num_points_to_draw > 1 else inner_graph_width # 점 하나면 간격 없음

            points = []
            for i, pop_count in enumerate(data_to_plot):
                x = inner_graph_x + i * point_spacing_x
                y_val_norm = pop_count / max_pop_overall if max_pop_overall > 0 else 0
                y = inner_graph_y + inner_graph_height * (1 - y_val_norm)
                points.append((x, y))
            
            if len(points) >= 2:
                pygame.draw.lines(surface_to_draw_on, line_color, False, points, const.GRAPH_LINE_THICKNESS)
            elif len(points) == 1 and full_history_mode: # 데이터 포인트가 하나일 때 점 찍기 (저장용)
                 pygame.draw.circle(surface_to_draw_on, line_color, points[0], const.GRAPH_LINE_THICKNESS)


        # 레이블 및 제목 (그래프 폰트 사용)
        font_to_use = self.graph_font
        title_text = f"Mode: {self.graph_mode.upper() if not full_history_mode else 'ALL (Full History)'}"
        title_surf = font_to_use.render(title_text, True, const.GRAPH_TEXT_COLOR)
        surface_to_draw_on.blit(title_surf, (graph_rect.centerx - title_surf.get_width() // 2, graph_rect.top + 5))

        max_pop_text = f"Max: {max_pop_overall}" # Y축 최대값
        max_pop_surf = font_to_use.render(max_pop_text, True, const.GRAPH_TEXT_COLOR)
        surface_to_draw_on.blit(max_pop_surf, (inner_graph_x + 5, graph_rect.top + 5)) # 그래프 영역 내부 좌상단

        x_label_text = "Time (Ticks)"
        x_label_surf = font_to_use.render(x_label_text, True, const.GRAPH_TEXT_COLOR)
        surface_to_draw_on.blit(x_label_surf, (graph_rect.centerx - x_label_surf.get_width() // 2, graph_rect.bottom - const.GRAPH_PADDING - x_label_surf.get_height() + 5 ))

        y_label_text = "Population"
        y_label_surf = font_to_use.render(y_label_text, True, const.GRAPH_TEXT_COLOR)
        y_label_surf_rotated = pygame.transform.rotate(y_label_surf, 90)
        surface_to_draw_on.blit(y_label_surf_rotated, (graph_rect.left + 5, graph_rect.centery - y_label_surf_rotated.get_height() // 2))


    def _draw_hud(self):
        hud_rect = const.HUD_AREA_RECT
        # pygame.draw.rect(self.screen, (30,30,30), hud_rect) # Optional HUD background

        status_text = "Status: Running"
        if self.is_paused:
            status_text = "Status: Paused"
        else:
            status_text += f" (Speed: x{self.simulation_speed_factor:.1f})"
        
        hud_info = [
            status_text, # 시뮬레이션 상태 추가
            f"Tick: {self.current_tick}",
            f"Global Energy: {self.global_energy_pool:.2f}",
            f"A: {len(self.creatures_a)} (L: {self.species_luck['A']:.2f})",
            f"B: {len(self.creatures_b)} (L: {self.species_luck['B']:.2f})",
            f"C: {len(self.creatures_c)} (L: {self.species_luck['C']:.2f})"
        ]
        for i, line in enumerate(hud_info):
            text_surface = self.hud_font.render(line, True, const.GREY)
            self.screen.blit(text_surface, (hud_rect.left + 5, hud_rect.top + 5 + i * (const.HUD_FONT_SIZE // 1.2))) # 간격 약간 조정


    def _save_graph_as_image(self):
        """현재까지 기록된 전체 개체 수 변화 그래프를 이미지 파일로 저장합니다."""
        if not any(self.population_history.values()):
            print("Graph Save: No population data to save.")
            return

        # 전체 히스토리 데이터 사용
        full_history = self.population_history
        
        # 저장될 그래프의 너비 동적 계산 또는 기본값 사용
        max_ticks_recorded = 0
        for species_key in full_history:
            max_ticks_recorded = max(max_ticks_recorded, len(full_history[species_key]))
        
        if max_ticks_recorded == 0:
            print("Graph Save: History is empty.")
            return

        # X축 픽셀당 틱 간격에 따른 너비 계산
        graph_width = const.GRAPH_SAVE_DEFAULT_WIDTH
        if const.GRAPH_SAVE_X_PIXELS_PER_TICK > 0:
            graph_width = max_ticks_recorded * const.GRAPH_SAVE_X_PIXELS_PER_TICK + const.GRAPH_PADDING * 6 # 충분한 여백 확보
            graph_width = max(graph_width, const.GRAPH_SAVE_DEFAULT_WIDTH) # 최소 너비 보장
        
        graph_height = const.GRAPH_SAVE_DEFAULT_HEIGHT
        
        # 그래프를 그릴 새로운 Surface 생성
        save_surface = pygame.Surface((graph_width, graph_height))
        save_surface.fill(const.GRAPH_BG_COLOR) # 배경색 채우기
        
        # 그래프 영역 Rect 정의 (Surface 전체 사용)
        save_graph_rect = save_surface.get_rect()
        
        # 이 Surface에 전체 데이터를 사용하여 그래프 그리기
        # _draw_population_graph 메서드 재활용 (full_history_mode=True)
        self._draw_population_graph(target_surface=save_surface, 
                                    history_data=full_history, 
                                    graph_rect_override=save_graph_rect, 
                                    full_history_mode=True)
        
        # 파일명 생성 및 저장
        if not os.path.exists(const.GRAPH_SAVE_PATH):
            try:
                os.makedirs(const.GRAPH_SAVE_PATH)
                print(f"Created directory: {const.GRAPH_SAVE_PATH}")
            except OSError as e:
                print(f"Error creating directory {const.GRAPH_SAVE_PATH}: {e}")
                return

        filename = f"{const.GRAPH_FILENAME_PREFIX}{self.current_tick}.png"
        full_path = os.path.join(const.GRAPH_SAVE_PATH, filename)
        
        try:
            pygame.image.save(save_surface, full_path)
            print(f"Graph saved to {full_path}")
        except pygame.error as e:
            print(f"Error saving graph to {full_path}: {e}")


    def _render(self): # 기존 로직과 거의 동일, HUD/그래프 영역 분리 명확화
        self.screen.fill(const.BLACK)
        
        # 시뮬레이션 영역 그리기 (개체들)
        # Creatures는 이미 SIMULATION_AREA_WIDTH 내로 confine됨
        for creature_list in [self.creatures_a, self.creatures_b, self.creatures_c]:
            for creature in creature_list:
                creature.draw(self.screen)
        
        self._draw_hud()
        self._draw_population_graph() # 화면 표시용 그래프

        pygame.display.flip()

    def run(self):
        self.is_running = True
        self.last_simulation_update_time = pygame.time.get_ticks()

        while self.is_running:
            self._handle_events()
            
            current_time_ms = pygame.time.get_ticks()
            
            # 틱 진행 시간 간격 계산 (속도 조절 반영)
            # self.simulation_speed_factor가 0이 되는 경우 방지 (최소 0.1배속 등으로)
            effective_speed_factor = max(0.1, self.simulation_speed_factor) # 0으로 나누기 방지
            tick_interval_ms = (const.SIMULATION_TICK_RATE / effective_speed_factor) * 1000
            
            if not self.is_paused: # 정지 상태가 아닐 때만 시뮬레이션 틱 진행
                if (current_time_ms - self.last_simulation_update_time) >= tick_interval_ms:
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