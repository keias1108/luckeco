# simulation.py
import pygame
import random
import math
import os
import time
import constants as const
from creatures import (CreatureA, CreatureB, CreatureC, 
                       CreatureD, CreatureE, CreatureF, 
                       CreatureG, CreatureH, CreatureI)

class Simulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
        pygame.display.set_caption("Ecosystem Simulation - 9 Species Fixed")
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
        
        # 모든 종의 리스트 속성 정의
        self.creatures_a = []
        self.creatures_b = []
        self.creatures_c = []
        self.creatures_d = []
        self.creatures_e = []
        self.creatures_f = []
        self.creatures_g = []
        self.creatures_h = []
        self.creatures_i = []

        # 모든 종에 대한 species_luck 및 population_history 초기화
        self.species_ids = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        self.species_luck = {sid: const.LUCK_DEFAULT for sid in self.species_ids}
        self.population_history = {sid: [] for sid in self.species_ids}
        
        self.current_tick = 0
        self.last_simulation_update_time = pygame.time.get_ticks()
        self.is_running = False

        self.graph_mode = 'all' # 그래프 모드는 A, B, C 또는 all 만 지원 (지시사항)
        self.graph_surface_rect = pygame.Rect(
            const.GRAPH_AREA_X_START, const.GRAPH_PADDING,
            const.GRAPH_AREA_WIDTH, const.SCREEN_HEIGHT - (2 * const.GRAPH_PADDING)
        )

        self.is_paused = False
        self.speed_factor_index = 0
        self.current_simulation_speed_factor = const.FAST_FORWARD_FACTORS[self.speed_factor_index]

        self._create_initial_creatures()

    def _get_random_position(self, radius):
        x = random.uniform(radius, const.SIMULATION_AREA_WIDTH - radius)
        y = random.uniform(radius, const.SIMULATION_AREA_HEIGHT - radius)
        return x, y

    def _create_initial_creatures(self):
        # A, B, C 초기화
        for _ in range(const.CREATURE_A_INITIAL_COUNT):
            x,y=self._get_random_position(const.CREATURE_A_RADIUS); self.creatures_a.append(CreatureA(x,y,self.species_luck['A']))
        for _ in range(const.CREATURE_B_INITIAL_COUNT):
            x,y=self._get_random_position(const.CREATURE_B_RADIUS); self.creatures_b.append(CreatureB(x,y,self.species_luck['B']))
        for _ in range(const.CREATURE_C_INITIAL_COUNT):
            x,y=self._get_random_position(const.CREATURE_C_RADIUS); self.creatures_c.append(CreatureC(x,y,self.species_luck['C']))
        # D ~ I 초기화
        for _ in range(const.CREATURE_D_INITIAL_COUNT):
            x,y=self._get_random_position(const.CREATURE_D_RADIUS); self.creatures_d.append(CreatureD(x,y,self.species_luck['D']))
        for _ in range(const.CREATURE_E_INITIAL_COUNT):
            x,y=self._get_random_position(const.CREATURE_E_RADIUS); self.creatures_e.append(CreatureE(x,y,self.species_luck['E']))
        for _ in range(const.CREATURE_F_INITIAL_COUNT):
            x,y=self._get_random_position(const.CREATURE_F_RADIUS); self.creatures_f.append(CreatureF(x,y,self.species_luck['F']))
        for _ in range(const.CREATURE_G_INITIAL_COUNT):
            x,y=self._get_random_position(const.CREATURE_G_RADIUS); self.creatures_g.append(CreatureG(x,y,self.species_luck['G']))
        for _ in range(const.CREATURE_H_INITIAL_COUNT):
            x,y=self._get_random_position(const.CREATURE_H_RADIUS); self.creatures_h.append(CreatureH(x,y,self.species_luck['H']))
        for _ in range(const.CREATURE_I_INITIAL_COUNT):
            x,y=self._get_random_position(const.CREATURE_I_RADIUS); self.creatures_i.append(CreatureI(x,y,self.species_luck['I']))


    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0 or event.key == pygame.K_BACKQUOTE: self.graph_mode = 'all'
                elif event.key == pygame.K_1: self.graph_mode = 'A'
                elif event.key == pygame.K_2: self.graph_mode = 'B'
                elif event.key == pygame.K_3: self.graph_mode = 'C'
                # D~I 개별 그래프 모드 키는 추가하지 않음 (지시사항)
                elif event.key == pygame.K_SPACE: self.is_paused = not self.is_paused
                elif event.key == pygame.K_RIGHT:
                    self.speed_factor_index = (self.speed_factor_index + 1) % len(const.FAST_FORWARD_FACTORS)
                    self.current_simulation_speed_factor = const.FAST_FORWARD_FACTORS[self.speed_factor_index]
                elif event.key == pygame.K_s: self._save_graph_as_image()
                # K_n (새로운 종 추가) 키 이벤트 제거

    # _add_new_species 메서드 제거

    def _spawn_creature_a(self):
        if self.current_tick > 0 and self.current_tick % const.CREATURE_A_CREATION_PERIOD_TICKS == 0:
            num_to_create_a = max(0, int(const.CREATURE_A_BASE_CREATION_COUNT * self.species_luck['A']))
            for _ in range(num_to_create_a):
                if self.global_energy_pool >= const.CREATURE_A_CREATION_COST:
                    self.global_energy_pool -= const.CREATURE_A_CREATION_COST
                    x, y = self._get_random_position(const.CREATURE_A_RADIUS)
                    self.creatures_a.append(CreatureA(x, y, self.species_luck['A']))
                else: break

    def _update_species_actions(self, predators_list, prey_list_or_id_key, species_id_predator):
        """특정 포식자 종의 행동을 업데이트하는 일반화된 함수"""
        newly_born = []
        # prey_list_or_id_key가 문자열이면 self에서 해당 리스트를 가져옴. 아니면 직접 리스트로 간주.
        actual_prey_list = getattr(self, f"creatures_{prey_list_or_id_key.lower()}", []) \
                           if isinstance(prey_list_or_id_key, str) else prey_list_or_id_key

        for predator in predators_list:
            if predator.is_alive:
                target = predator.find_target(actual_prey_list)
                predator.move(target)
                if target and target.is_alive:
                    predator.hunt(target)
                
                if predator.can_reproduce():
                    offspring = predator.attempt_reproduction()
                    if offspring:
                        offspring.luck = self.species_luck[species_id_predator]
                        newly_born.append(offspring)
        predators_list.extend(newly_born)


    def _update_creatures_actions(self):
        self._update_species_actions(self.creatures_b, self.creatures_a, 'B') # B hunts A
        self._update_species_actions(self.creatures_c, self.creatures_b, 'C') # C hunts B
        self._update_species_actions(self.creatures_d, self.creatures_c, 'D') # D hunts C
        self._update_species_actions(self.creatures_e, self.creatures_d, 'E') # E hunts D
        self._update_species_actions(self.creatures_f, self.creatures_e, 'F') # F hunts E
        self._update_species_actions(self.creatures_g, self.creatures_f, 'G') # G hunts F
        self._update_species_actions(self.creatures_h, self.creatures_g, 'H') # H hunts G
        self._update_species_actions(self.creatures_i, self.creatures_h, 'I') # I hunts H


    def _get_all_creature_lists(self):
        """모든 종의 개체 리스트를 반환합니다."""
        return [
            self.creatures_a, self.creatures_b, self.creatures_c,
            self.creatures_d, self.creatures_e, self.creatures_f,
            self.creatures_g, self.creatures_h, self.creatures_i
        ]

    def _update_creatures_age(self):
        for creature_list in self._get_all_creature_lists():
            for creature in creature_list:
                creature.update_age()

    def _process_deaths_and_energy_return(self):
        all_species_data = {
            'A': self.creatures_a, 'B': self.creatures_b, 'C': self.creatures_c,
            'D': self.creatures_d, 'E': self.creatures_e, 'F': self.creatures_f,
            'G': self.creatures_g, 'H': self.creatures_h, 'I': self.creatures_i
        }
        new_creature_lists = {sid: [] for sid in self.species_ids}

        for species_id, creature_list in all_species_data.items():
            for creature in creature_list:
                if creature.is_alive:
                    new_creature_lists[species_id].append(creature)
                else:
                    if creature.age_ticks >= const.CREATURE_LIFESPAN_TICKS:
                        self.global_energy_pool += creature.current_energy_level
        
        self.creatures_a = new_creature_lists['A']
        self.creatures_b = new_creature_lists['B']
        self.creatures_c = new_creature_lists['C']
        self.creatures_d = new_creature_lists['D']
        self.creatures_e = new_creature_lists['E']
        self.creatures_f = new_creature_lists['F']
        self.creatures_g = new_creature_lists['G']
        self.creatures_h = new_creature_lists['H']
        self.creatures_i = new_creature_lists['I']

    def _update_luck_system(self):
        if self.current_tick > 0 and self.current_tick % const.LUCK_ADJUSTMENT_PERIOD_TICKS == 0:
            # 모든 종의 개체 수 계산
            populations = {sid: len(getattr(self, f"creatures_{sid.lower()}")) for sid in self.species_ids}
            total_creatures = sum(populations.values())

            if total_creatures > 0:
                shares = {sid: pop / total_creatures for sid, pop in populations.items()}
                
                target_shares = {
                    'A': const.TARGET_RATIO_A_SHARE, 'B': const.TARGET_RATIO_B_SHARE,
                    'C': const.TARGET_RATIO_C_SHARE, 'D': const.TARGET_RATIO_D_SHARE,
                    'E': const.TARGET_RATIO_E_SHARE, 'F': const.TARGET_RATIO_F_SHARE,
                    'G': const.TARGET_RATIO_G_SHARE, 'H': const.TARGET_RATIO_H_SHARE,
                    'I': const.TARGET_RATIO_I_SHARE
                }

                for sid in self.species_ids:
                    delta = target_shares[sid] - shares[sid]
                    self.species_luck[sid] = max(const.LUCK_MIN, min(const.LUCK_MAX, 
                                               self.species_luck[sid] + (delta * const.LUCK_ADJUSTMENT_K_FACTOR)))
            else: # 모든 종이 없으면 기본 운으로
                self.species_luck = {sid: const.LUCK_DEFAULT for sid in self.species_ids}
            
            # 모든 개체에 운 적용
            all_creature_lists_with_ids = [
                (self.creatures_a, 'A'), (self.creatures_b, 'B'), (self.creatures_c, 'C'),
                (self.creatures_d, 'D'), (self.creatures_e, 'E'), (self.creatures_f, 'F'),
                (self.creatures_g, 'G'), (self.creatures_h, 'H'), (self.creatures_i, 'I')
            ]
            for creature_list, species_id_key in all_creature_lists_with_ids:
                for creature in creature_list:
                    creature.luck = self.species_luck[species_id_key]


    def _update_population_history(self):
        for sid in self.species_ids:
            self.population_history[sid].append(len(getattr(self, f"creatures_{sid.lower()}")))

        if const.GRAPH_MAX_HISTORY > 0:
            for key in self.population_history:
                while len(self.population_history[key]) > const.GRAPH_MAX_HISTORY:
                    self.population_history[key].pop(0)
    
    def _draw_population_graph(self, target_surface=None, history_data_override=None, graph_rect_override=None, full_history_mode=False):
        surface_to_draw_on = target_surface if target_surface else self.screen
        current_history_source = history_data_override if history_data_override else self.population_history
        graph_rect = graph_rect_override if graph_rect_override else self.graph_surface_rect

        pygame.draw.rect(surface_to_draw_on, const.GRAPH_BG_COLOR, graph_rect)
        pygame.draw.rect(surface_to_draw_on, const.GRAPH_AXIS_COLOR, graph_rect, 1)

        species_map = {
            'A': (const.GRAPH_LINE_COLOR_A, current_history_source.get('A', [])),
            'B': (const.GRAPH_LINE_COLOR_B, current_history_source.get('B', [])),
            'C': (const.GRAPH_LINE_COLOR_C, current_history_source.get('C', [])),
            'D': (const.GRAPH_LINE_COLOR_D, current_history_source.get('D', [])),
            'E': (const.GRAPH_LINE_COLOR_E, current_history_source.get('E', [])),
            'F': (const.GRAPH_LINE_COLOR_F, current_history_source.get('F', [])),
            'G': (const.GRAPH_LINE_COLOR_G, current_history_source.get('G', [])),
            'H': (const.GRAPH_LINE_COLOR_H, current_history_source.get('H', [])),
            'I': (const.GRAPH_LINE_COLOR_I, current_history_source.get('I', []))
        }
        
        active_keys_to_draw = []
        if self.graph_mode == 'all' or full_history_mode:
            active_keys_to_draw = self.species_ids # 모든 종을 그림
        elif self.graph_mode in ['A', 'B', 'C']: # 개별 모드는 A, B, C만 지원
            active_keys_to_draw = [self.graph_mode]
        else: # 그 외의 경우 (예: self.graph_mode가 D, E.. 로 설정될 수 있는 키가 없다면)
             active_keys_to_draw = [] # 또는 'all'로 기본 설정

        has_data_to_draw = False
        for key in active_keys_to_draw:
            if key in species_map and species_map[key][1]:
                has_data_to_draw = True; break
        if not has_data_to_draw: return

        max_pop_overall = 1; max_history_len_for_scale = 0
        for key in active_keys_to_draw:
            if key not in species_map: continue
            history = species_map[key][1]
            if history:
                max_pop_overall = max(max_pop_overall, max(history))
                max_history_len_for_scale = max(max_history_len_for_scale, len(history))
        
        if max_history_len_for_scale < (1 if full_history_mode and max_history_len_for_scale == 1 else 2) : return

        y_axis_label_space = const.GRAPH_PADDING*2 + self.graph_font.get_height()
        x_axis_label_space = const.GRAPH_PADDING*2 + self.graph_font.get_height()
        title_space = const.GRAPH_PADDING + self.graph_font.get_height() + 5
        legend_space_per_item = self.graph_font.get_height() + 2
        max_pop_text_height = self.graph_font.get_height() + 5


        inner_graph_x = graph_rect.left + y_axis_label_space
        inner_graph_y = graph_rect.top + title_space + max_pop_text_height # 제목 및 Max Pop 위한 공간
        
        # 범례가 너무 길어지면 그래프 영역 침범 가능, 저장 시에는 범례 위치 조정 또는 별도 영역 필요
        available_legend_height = graph_rect.height - (title_space + max_pop_text_height + x_axis_label_space + const.GRAPH_PADDING)
        num_legend_items_can_fit = available_legend_height // legend_space_per_item

        inner_graph_width = graph_rect.width - y_axis_label_space - const.GRAPH_PADDING
        # 범례 공간을 위해 그래프 높이 조정 (화면 표시 시)
        if not full_history_mode and (self.graph_mode == 'all' or len(active_keys_to_draw) > 1) :
             # 화면 표시용 'all' 모드일 때만 범례 공간 확보
             legend_total_height = len(active_keys_to_draw) * legend_space_per_item
             inner_graph_height = graph_rect.height - title_space - max_pop_text_height - x_axis_label_space - const.GRAPH_PADDING - legend_total_height
        else:
             inner_graph_height = graph_rect.height - title_space - max_pop_text_height - x_axis_label_space - const.GRAPH_PADDING



        if inner_graph_width <=10 or inner_graph_height <=10: return

        pygame.draw.line(surface_to_draw_on, const.GRAPH_AXIS_COLOR, (inner_graph_x, inner_graph_y + inner_graph_height), (inner_graph_x + inner_graph_width, inner_graph_y + inner_graph_height), 1)
        pygame.draw.line(surface_to_draw_on, const.GRAPH_AXIS_COLOR, (inner_graph_x, inner_graph_y), (inner_graph_x, inner_graph_y + inner_graph_height), 1)

        for key in active_keys_to_draw:
            if key not in species_map: continue
            line_color, history = species_map[key]
            data_to_plot = history
            if not full_history_mode and const.GRAPH_MAX_HISTORY > 0 and len(history) > const.GRAPH_MAX_HISTORY:
                data_to_plot = history[-const.GRAPH_MAX_HISTORY:]
            num_points_to_draw = len(data_to_plot)
            if num_points_to_draw < (1 if full_history_mode and num_points_to_draw == 1 else 2): continue
            point_spacing_x = inner_graph_width/(num_points_to_draw-1) if num_points_to_draw > 1 else 0
            points = []
            for i, pop_count in enumerate(data_to_plot):
                x = inner_graph_x + (i * point_spacing_x if num_points_to_draw > 1 else 0)
                y_val_norm = pop_count / max_pop_overall if max_pop_overall > 0 else 0
                y = inner_graph_y + inner_graph_height * (1 - y_val_norm)
                points.append((x, y))
            if len(points) >= 2: pygame.draw.lines(surface_to_draw_on, line_color, False, points, const.GRAPH_LINE_THICKNESS)
            elif len(points) == 1: pygame.draw.circle(surface_to_draw_on, line_color, points[0], const.GRAPH_LINE_THICKNESS +1)

        font_to_use = self.graph_font
        graph_mode_display = self.graph_mode
        if full_history_mode: graph_mode_display = 'ALL (Saved)'
        elif self.graph_mode not in ['A', 'B', 'C']: graph_mode_display = 'ALL'
        
        title_text_content = f"Mode: {graph_mode_display.upper()}"
        if full_history_mode: title_text_content = f"Full History (Tick: {self.current_tick})"
        title_surf = font_to_use.render(title_text_content, True, const.GRAPH_TEXT_COLOR)
        surface_to_draw_on.blit(title_surf, (graph_rect.centerx - title_surf.get_width() // 2, graph_rect.top + 5))

        max_pop_text = f"Max: {max_pop_overall}"
        max_pop_surf = font_to_use.render(max_pop_text, True, const.GRAPH_TEXT_COLOR)
        surface_to_draw_on.blit(max_pop_surf, (inner_graph_x + 5, graph_rect.top + 5 + title_surf.get_height()))

        x_label_text = "Time (Ticks)"
        x_label_surf = font_to_use.render(x_label_text, True, const.GRAPH_TEXT_COLOR)
        surface_to_draw_on.blit(x_label_surf, (graph_rect.centerx - x_label_surf.get_width() // 2, graph_rect.bottom - const.GRAPH_PADDING - x_label_surf.get_height() + 5 ))

        y_label_text = "Population"
        y_label_surf = font_to_use.render(y_label_text, True, const.GRAPH_TEXT_COLOR)
        y_label_surf_rotated = pygame.transform.rotate(y_label_surf, 90)
        surface_to_draw_on.blit(y_label_surf_rotated, (graph_rect.left + 5, graph_rect.centery - y_label_surf_rotated.get_height() // 2))
        
        # 범례 (화면 표시 시, 공간이 협소하면 일부만 표시하거나 다르게 배치)
        if not full_history_mode and (self.graph_mode == 'all' or len(active_keys_to_draw) > 1):
            legend_y_start = graph_rect.bottom - const.GRAPH_PADDING - x_axis_label_space - const.GRAPH_PADDING  # X축 위, 패딩 고려
            max_legend_items_fit_on_screen = 4 # 예시, 화면 공간에 따라 조절
            
            items_drawn = 0
            for key in active_keys_to_draw: # 모든 활성 키에 대해 시도
                if items_drawn >= max_legend_items_fit_on_screen and len(active_keys_to_draw) > max_legend_items_fit_on_screen:
                    # "et al." 또는 "..." 같은 표시 추가 가능
                    etc_surf = font_to_use.render("...", True, const.GRAPH_TEXT_COLOR)
                    surface_to_draw_on.blit(etc_surf, (inner_graph_x + 5, legend_y_start - (items_drawn * legend_space_per_item) ))
                    break

                if key in species_map:
                    color, _ = species_map[key]
                    legend_text = f"{key}"
                    legend_surf = font_to_use.render(legend_text, True, color)
                    current_legend_y = legend_y_start - (items_drawn * legend_space_per_item) - legend_surf.get_height()
                    if current_legend_y < inner_graph_y : continue # 그래프 영역 침범 방지

                    surface_to_draw_on.blit(legend_surf, (inner_graph_x + 5, current_legend_y))
                    pygame.draw.line(surface_to_draw_on, color, 
                                     (inner_graph_x + legend_surf.get_width() + 10, current_legend_y + legend_surf.get_height()//2), 
                                     (inner_graph_x + legend_surf.get_width() + 30, current_legend_y + legend_surf.get_height()//2), 2)
                    items_drawn += 1
        elif full_history_mode : # 저장시 범례
            legend_y_start = graph_rect.top + title_space + max_pop_text_height + const.GRAPH_PADDING
            legend_x_start = inner_graph_x + inner_graph_width + const.GRAPH_PADDING # 그래프 오른쪽에 범례 표시 (공간이 있다면)
            if legend_x_start + 100 > graph_rect.right : # 공간 부족 시 그래프 아래쪽
                 legend_x_start = inner_graph_x
                 legend_y_start = inner_graph_y + inner_graph_height + const.GRAPH_PADDING + 5

            for key in self.species_ids: # 저장 시 모든 종 범례
                if key in species_map:
                    color, _ = species_map[key]
                    legend_text = f"{key}"
                    legend_surf = font_to_use.render(legend_text, True, color)
                    if legend_y_start + legend_surf.get_height() > graph_rect.bottom - const.GRAPH_PADDING: # 범례가 영역을 벗어나면 중단
                        break 
                    surface_to_draw_on.blit(legend_surf, (legend_x_start, legend_y_start))
                    pygame.draw.line(surface_to_draw_on, color, 
                                     (legend_x_start + legend_surf.get_width() + 5, legend_y_start + legend_surf.get_height()//2), 
                                     (legend_x_start + legend_surf.get_width() + 25, legend_y_start + legend_surf.get_height()//2), 2)
                    legend_y_start += legend_surf.get_height() + 2



    def _draw_hud(self):
        hud_rect = const.HUD_AREA_RECT
        status_text = "Status: Paused" if self.is_paused else f"Status: Running (Speed: x{self.current_simulation_speed_factor:.1f})"
        
        base_hud_info = [
            status_text, f"Tick: {self.current_tick}", f"Energy: {self.global_energy_pool:.2f}"
        ]
        
        y_offset = hud_rect.top + 5
        line_height = const.HUD_FONT_SIZE * 0.8 # 줄 간격 조정을 위해 사용

        for line in base_hud_info:
            text_surface = self.hud_font.render(line, True, const.GREY)
            self.screen.blit(text_surface, (hud_rect.left + 5, y_offset ))
            y_offset += line_height
        
        y_offset += 5 # 섹션 간 간격

        # 종별 정보 표시 (2열로 나누어 표시 시도)
        column_width = hud_rect.width // 2 - 10
        current_column_x = hud_rect.left + 5
        start_y_for_species = y_offset

        for i, species_id in enumerate(self.species_ids):
            pop_count = len(getattr(self, f"creatures_{species_id.lower()}"))
            luck_val = self.species_luck.get(species_id, const.LUCK_DEFAULT)
            species_text = f"{species_id}: {pop_count} (L: {luck_val:.2f})"
            text_surface = self.hud_font.render(species_text, True, const.GREY)
            
            if y_offset + line_height > hud_rect.bottom - 5 : # HUD 영역을 벗어나면 다음 열로
                 current_column_x += column_width
                 y_offset = start_y_for_species
                 if current_column_x + column_width > hud_rect.right: # 두 번째 열도 꽉차면 중단
                      break

            self.screen.blit(text_surface, (current_column_x, y_offset))
            y_offset += line_height


    def _save_graph_as_image(self):
        history_to_save = self.population_history
        if not any(any(hist_list) for hist_list in history_to_save.values()):
            print("Graph Save: No population data to save."); return

        max_ticks_recorded = 0
        for history_list in history_to_save.values(): max_ticks_recorded = max(max_ticks_recorded, len(history_list))
        if max_ticks_recorded == 0: print("Graph Save: History is empty."); return

        save_width = const.GRAPH_SAVE_DEFAULT_WIDTH
        if const.GRAPH_SAVE_X_PIXELS_PER_TICK > 0 and max_ticks_recorded > 0 :
            potential_width = max_ticks_recorded * const.GRAPH_SAVE_X_PIXELS_PER_TICK + const.GRAPH_PADDING * 10 # 넓은 패딩
            save_width = max(potential_width, const.GRAPH_SAVE_DEFAULT_WIDTH)
        save_height = const.GRAPH_SAVE_DEFAULT_HEIGHT
        
        save_surface = pygame.Surface((save_width, save_height))
        save_surface.fill(const.GRAPH_BG_COLOR)
        save_graph_rect = save_surface.get_rect()
        
        original_graph_mode = self.graph_mode # 현재 그래프 모드 저장
        self.graph_mode = 'all' # 저장 시에는 모든 종을 그리기 위해 임시 변경
        
        self._draw_population_graph(target_surface=save_surface, 
                                    history_data_override=history_to_save, 
                                    graph_rect_override=save_graph_rect, 
                                    full_history_mode=True)
        
        self.graph_mode = original_graph_mode # 원래 그래프 모드로 복원

        if not os.path.exists(const.GRAPH_SAVE_PATH):
            try: os.makedirs(const.GRAPH_SAVE_PATH, exist_ok=True)
            except OSError as e: print(f"Error creating directory {const.GRAPH_SAVE_PATH}: {e}"); return

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{const.GRAPH_FILENAME_PREFIX}{self.current_tick}_{timestamp}.png"
        full_path = os.path.join(const.GRAPH_SAVE_PATH, filename)
        try: pygame.image.save(save_surface, full_path); print(f"Graph saved to {full_path}")
        except pygame.error as e: print(f"Error saving graph to {full_path}: {e}")


    def _render(self):
        self.screen.fill(const.BLACK)
        # 모든 종 개체 그리기
        for creature_list in self._get_all_creature_lists():
            for creature in creature_list: creature.draw(self.screen)
        self._draw_hud()
        self._draw_population_graph()
        pygame.display.flip()

    def run(self):
        self.is_running = True
        self.last_simulation_update_time = pygame.time.get_ticks()

        while self.is_running:
            self._handle_events()
            current_time_ms = pygame.time.get_ticks()
            effective_speed_factor = max(0.01, self.current_simulation_speed_factor)
            tick_interval_ms = (const.SIMULATION_TICK_RATE / effective_speed_factor) * 1000
            
            if not self.is_paused:
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