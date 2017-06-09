# David Chen and Brian Yeh - CS440 Spring 2017

from random import choice, randint, random
from win32api import GetSystemMetrics
import pygame
from datetime import datetime
from utils.colors import *
from utils.helper_defs import *
from utils.helper_defs import round_down_to_multiple as RDTM, euclidean_dist as E_dist, manhattan_dist as M_dist, \
                              change_direction as CD, chebyshev_dist as C_dist, our_inadmissible_dist as In_dist, \
                              our_admissible_dist as A_dist
from utils.a_star import *

SYSTEM_WIDTH = GetSystemMetrics(0)
SYSTEM_HEIGHT = GetSystemMetrics(1)
# print(SYSTEM_WIDTH, SYSTEM_HEIGHT)
# maps need to be 160 columns by 120 rows so the aspect ratio is 4:3 and thus landscape mode, wide > tall
GRID_BLOCKS_TALL = 120
GRID_BLOCKS_WIDE = 160

# assume screen to be landscape, so map height = map width = screen height, which is the lower pixel count
MAP_HEIGHT = SYSTEM_HEIGHT
SCALE = int(SYSTEM_HEIGHT / GRID_BLOCKS_TALL)
MAP_WIDTH = SCALE * GRID_BLOCKS_WIDE

INTERFACE_HEIGHT = MAP_HEIGHT
INTERFACE_WIDTH = SYSTEM_WIDTH - MAP_WIDTH
INTERFACE_PADDING = SCALE

# print(MAP_WIDTH,MAP_HEIGHT,INTERFACE_HEIGHT,INTERFACE_WIDTH,INTERFACE_PADDING)

NUMBER_OF_HTT_AREAS = 8
NUMBER_OF_RIVERS = 4
NUMBER_OF_BLOCKED_CELLS = int(GRID_BLOCKS_WIDE*GRID_BLOCKS_TALL*.2)

DEFAULT_BORDER_COLOR = LIGHT_GRAY
FONT_SIZE = 15
FONT = None
INTERNAL_MAP = []  # internal map (list of lists)
EXTERNAL_MAP_BASE = None  # map visual with no goals
EXTERNAL_MAP_FULL = None  # map visual with goals and all
START_NODE = None
GOAL_NODE = None
MAIN_SCREEN = None
GRAPH = None

H = A_dist
WEIGHTS = [1.25, 1.25, 1.25]
W_SELECTION = ['<<', '', '']
W_INDEX = 0
HTT_COORDS = None

H_DEFS = {
    0: A_dist,
    1: M_dist,
    2: E_dist,
    3: C_dist,
    4: In_dist
}

# cell types
# blocked = 0
# regular unblocked = 1
# hard to traverse = 2

class Cell(object):
    def __init__(self, pixel_x, pixel_y, row, col, c_type):
        self.pixel_x = int(pixel_x)
        self.pixel_y = int(pixel_y)
        self.row = int(row)
        self.col = int(col)
        self.c_type = int(c_type)
        self.is_highway = self.is_start = self.is_goal = self.in_fringe = self.expanded_already = False
        self.parent = None
        self.neighbors = []
        self.g_value = self.h_value = None
        if self.g_value and self.h_value:
            self.f_value = self.g_value + self.h_value
        else:
            self.f_value = None

    def get_color(self):
        if self.is_start:  # start cell
            return GREEN
        elif self.is_goal:  # goal cell
            return RED
        elif self.is_highway:  # is highway and is...
            if self.c_type == 1:   # normal cell
                return CYAN
            elif self.c_type == 2:  # HTT cell
                return DARK_CYAN
        elif self.c_type == 0:  # blocked cell
            return BLACK
        elif self.c_type == 1:  # normal cell
            return WHITE
        elif self.c_type == 2:  # HTT cell
            return BROWN
        else:  # unknown cell
            return YELLOW

    def get_type_string(self):
        if self.is_start:
            return 'START CELL'
        elif self.is_goal:
            return 'GOAL CELL'
        elif self.is_highway:  # is highway and is...
            if self.c_type == 1:  # normal cell
                return 'NORMAL HIGHWAY CELL'
            elif self.c_type == 2:  # HTT cell
                return 'HTT HIGHWAY CELL'
        elif self.c_type == 0:  # blocked cell
            return 'BLOCKED CELL'
        elif self.c_type == 1:  # normal cell
            return 'NORMAL CELL'
        elif self.c_type == 2:  # HTT cell
            return 'HTT CELL'
        else:  # unknown cell
            return 'UNKNOWN CELL'

    def is_edge_cell(self):
        if self.row == 0 or self.row == GRID_BLOCKS_TALL - 1 or self.col == 0 or self.col == GRID_BLOCKS_WIDE - 1:
            return True
        else:
            return False


def load_user_interface():
    if H == C_dist:
        h_string = "CHEBYSHEV"
    elif H == M_dist:
        h_string = "MANHATTAN"
    elif H == E_dist:
        h_string = "EUCLIDEAN"
    elif H == In_dist:
        h_string = "INADMISSIBLE"
    elif H == A_dist:
        h_string = "ADMISSIBLE"
    else:
        h_string = "ERROR"

    instructs = []
    i_file = open('instructs.cs440', 'r')
    for line in i_file:
        instructs.append(line)
    i_file.close()

    i_w = INTERFACE_WIDTH
    i_h = INTERFACE_HEIGHT
    i_p = INTERFACE_PADDING
    pygame.draw.rect(MAIN_SCREEN, DARK_GRAY, (MAP_WIDTH, 0, i_w, i_h), 0)  # BORDER
    pygame.draw.rect(MAIN_SCREEN, WHITE, (MAP_WIDTH + i_p, i_p, i_w - 2 * i_p, i_h - 2 * i_p), 0)  # INNER

    padding = 25
    for i in instructs:
        current_i = i.strip()

        if current_i == '[CURRENT H]':
            current_i = 'CURRENT HEURISTIC: {}'.format(h_string)

        elif current_i == '[CURRENT A*w]':
            current_i = 'WEIGHTED A* WEIGHT: {} {}'.format(WEIGHTS[0], W_SELECTION[0])
        elif current_i == '[CURRENT w1]':
            current_i = 'SEQ/INT\'D WEIGHT_1: {} {}'.format(WEIGHTS[1], W_SELECTION[1])
        elif current_i == '[CURRENT w2]':
            current_i = 'SEQ/INT\'D WEIGHT_2: {} {}'.format(WEIGHTS[2], W_SELECTION[2])

        text_surface = FONT.render('{}'.format(current_i), True, BLACK)
        MAIN_SCREEN.blit(text_surface, (MAP_WIDTH + i_p*2, i_p + padding, i_w - 2 * i_p, i_h - 2 * i_p))
        padding += 25

    pygame.display.update()
    return



def main():
    global FONT, MAIN_SCREEN, INTERNAL_MAP, H, WEIGHTS, W_INDEX, W_SELECTION

    pygame.init()
    MAIN_SCREEN = pygame.display.set_mode((SYSTEM_WIDTH, SYSTEM_HEIGHT), pygame.FULLSCREEN)
    icon = pygame.image.load('images/robot_icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('CS440 Assignment 1')
    FONT = pygame.font.SysFont("monospace", FONT_SIZE)

    load_user_interface()
    internal_grid, map_visual_base = generate_a_map()
    start, goal, map_visual_full = draw_get_start_and_goal(internal_grid, map_visual_base)
    save_the_map(internal_grid, start, goal, HTT_COORDS)
    pygame.display.update()
    previous_highlighted_cell = normal_color = highlighted_cell = None
    info_ready = False

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()

            if e.type == pygame.KEYDOWN:

                solution = []

                if e.key == pygame.K_c:  # clear labels, keep map and start/goal
                    MAIN_SCREEN.blit(map_visual_full, (0, 0))
                    load_user_interface()
                    pygame.display.update()
                if e.key == pygame.K_n:  # new map
                    internal_grid, map_visual_base = generate_a_map()
                    start, goal, map_visual_full = draw_get_start_and_goal(internal_grid, map_visual_base)
                    pygame.display.update()
                if e.key == pygame.K_g:  # new start/goal cells
                    start, goal, map_visual_full = draw_get_start_and_goal(internal_grid, map_visual_base)
                    pygame.display.update()

                if e.key == pygame.K_a:  # run a* normal
                    solution = a_star(start, goal, internal_grid, H)
                    path_color = GREEN
                if e.key == pygame.K_u:  # run UCS
                    solution = uniform_cost_search(start, goal, internal_grid)
                    path_color = PINK
                if e.key == pygame.K_w:  # run weighted A*
                    solution = weighted_a_star(start, goal, internal_grid, H, WEIGHTS[0])
                    path_color = PURPLE
                if e.key == pygame.K_s:  # run sequential A*
                    solution = sequential_a_star(start, goal, internal_grid, H_DEFS, WEIGHTS[1], WEIGHTS[2])
                    path_color = YELLOW
                if e.key == pygame.K_i:  # run integrated A*
                    solution = integrated_a_star(start, goal, internal_grid, H_DEFS, WEIGHTS[1], WEIGHTS[2])
                    path_color = RED
                if e.key == pygame.K_d:  # save the map to file
                    save_the_map(internal_grid, start, goal, HTT_COORDS)
                    pygame.display.update()
                if e.key == pygame.K_1:
                    H = C_dist
                    load_user_interface()
                if e.key == pygame.K_2:
                    H = M_dist
                    load_user_interface()
                if e.key == pygame.K_3:
                    H = E_dist
                    load_user_interface()
                if e.key == pygame.K_4:
                    H = In_dist
                    load_user_interface()
                if e.key == pygame.K_5:
                    H = A_dist
                    load_user_interface()

                if e.key == pygame.K_DOWN:
                    W_SELECTION[W_INDEX] = ''
                    if W_INDEX == 2:
                        W_INDEX = 0
                    else:
                        W_INDEX += 1
                    W_SELECTION[W_INDEX] = '<<'
                    load_user_interface()

                if e.key == pygame.K_UP:
                    W_SELECTION[W_INDEX] = ''
                    if W_INDEX == 0:
                        W_INDEX = 2
                    else:
                        W_INDEX -= 1
                    W_SELECTION[W_INDEX] = '<<'
                    load_user_interface()

                if e.key == pygame.K_LEFT:
                    WEIGHTS[W_INDEX] -= 0.25
                    load_user_interface()
                if e.key == pygame.K_RIGHT:
                    WEIGHTS[W_INDEX] += 0.25
                    load_user_interface()

                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

                if solution:
                    info_ready = True
                    for cell in solution:
                        tmp_sq = pygame.Surface((SCALE - 1, SCALE - 1))
                        tmp_sq.fill(path_color)
                        # tmp_sq.set_alpha(100)
                        MAIN_SCREEN.blit(tmp_sq, (cell.pixel_x + 1, cell.pixel_y + 1))
                        pygame.display.update()

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # if left mouse button clicked
                m_pos = pygame.mouse.get_pos()
                pix_x = m_pos[0]
                pix_y = m_pos[1]

                if pix_x < MAP_WIDTH and info_ready:  # means clicked within the map and not the interface
                    c_pix_x = RDTM(pix_x, SCALE)
                    c_pix_y = RDTM(pix_y, SCALE)

                    row = int(c_pix_y / SCALE)
                    col = int(c_pix_x / SCALE)
                    clicked_cell = internal_grid[row][col]
                    display_info(clicked_cell)
                else:
                    pass

            if e.type == pygame.MOUSEMOTION:
                m_pos = pygame.mouse.get_pos()
                pix_x = m_pos[0]
                pix_y = m_pos[1]

                if pix_x < MAP_WIDTH:  # means hovering within the map and not the interface
                    c_pix_x = RDTM(pix_x, SCALE)
                    c_pix_y = RDTM(pix_y, SCALE)
                    row = int(c_pix_y / SCALE)
                    col = int(c_pix_x / SCALE)

                    if highlighted_cell != internal_grid[row][col]:
                        highlighted_cell = internal_grid[row][col]

                        if previous_highlighted_cell:
                            if previous_highlighted_cell is not highlighted_cell:
                                draw_cell_rect(MAIN_SCREEN, normal_color, previous_highlighted_cell.pixel_x,
                                               previous_highlighted_cell.pixel_y, DEFAULT_BORDER_COLOR, 1)
                                pygame.display.update()

                        normal_color = MAIN_SCREEN.get_at((highlighted_cell.pixel_x + 5, highlighted_cell.pixel_y + 5))
                        draw_cell_rect(MAIN_SCREEN, YELLOW, highlighted_cell.pixel_x,
                                       highlighted_cell.pixel_y, DEFAULT_BORDER_COLOR, 1)
                        pygame.display.update()
                        previous_highlighted_cell = internal_grid[row][col]

                else:
                    pass

    return


def generate_a_map():
    # generates a new map without start and goal nodes
    # returns the internal grid representative of this map and the external visual of this base map

    map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA, 32)
    map_surface = map_surface.convert_alpha()

    grid = draw_init_grid(map_surface)
    draw_htt_areas_on_grid(map_surface, grid, NUMBER_OF_HTT_AREAS)
    draw_rivers_on_grid(map_surface, grid, NUMBER_OF_RIVERS)
    draw_blocked_cells_on_grid(map_surface, grid, NUMBER_OF_BLOCKED_CELLS)

    return grid, map_surface.copy()


def draw_init_grid(map_surface):
    grid_map = []

    for vertical_pixel in range(0, MAP_HEIGHT, SCALE):
        temp_row = []
        for horizontal_pixel in range(0, MAP_WIDTH, SCALE):
            temp_cell = Cell(horizontal_pixel, vertical_pixel, vertical_pixel / SCALE, horizontal_pixel / SCALE, 1)
            temp_row.append(temp_cell)
            draw_cell_rect(map_surface, temp_cell.get_color(), horizontal_pixel, vertical_pixel, DEFAULT_BORDER_COLOR, 1)
        grid_map.append(temp_row)

    MAIN_SCREEN.blit(map_surface, (0, 0))
    pygame.display.update()

    return grid_map


def draw_htt_areas_on_grid(map_surface, grid, num_htt_areas):
    global HTT_COORDS
    random_htt_area_coords = []

    while len(random_htt_area_coords) != num_htt_areas:
        htt_area_origin_column = randint(0, GRID_BLOCKS_WIDE - 1)
        htt_area_origin_row = randint(0, GRID_BLOCKS_TALL - 1)
        htt_area_origin_coords = [htt_area_origin_column, htt_area_origin_row]
        if htt_area_origin_coords not in random_htt_area_coords:
            random_htt_area_coords.append(htt_area_origin_coords)

    for coordinates in random_htt_area_coords:
        htt_col = coordinates[0]
        htt_row = coordinates[1]
        for tmp_col in range(htt_col-15, htt_col+16):
            for tmp_row in range(htt_row-15, htt_row+16):
                if tmp_col < 0 or tmp_col > GRID_BLOCKS_WIDE - 1 or tmp_row < 0 or tmp_row > GRID_BLOCKS_TALL - 1:
                    continue
                else:
                    if random() < 0.5:
                        tmp_cell = grid[tmp_row][tmp_col]
                        tmp_cell.c_type = 2  # set to HTT
                        draw_cell_rect(map_surface, tmp_cell.get_color(),
                                       tmp_cell.pixel_x, tmp_cell.pixel_y, DEFAULT_BORDER_COLOR, 1)

        MAIN_SCREEN.blit(map_surface, (0, 0))
        pygame.display.update()

    HTT_COORDS = random_htt_area_coords
    return


def draw_rivers_on_grid(map_surface, grid, num_rivers):

    for _ in range(num_rivers):
        valid_river = False
        drawing_q = []

        while not valid_river:
            # if not valid river...
            drawing_q = []  # reset the drawing queue
            river_origin_cell = get_riverless_edge_cell(grid)  # get a new river origin not on a river
            current_direction = river_start_direction(river_origin_cell)  # get direction to begin in
            drawing_q.append(river_origin_cell)
            edge_hit = False
            river_hit = False
            self_hit = False

            begin_direction = current_direction
            begin_cell = river_origin_cell

            while not edge_hit:
                mini_q = twenty_steps_in_direction(grid, begin_cell, begin_direction)
                if not mini_q:  # in the event the function above encountered another river, break and scrap
                    river_hit = True
                    break
                else:  # below here means the function made 20 steps or encountered an edge
                    for tmp_cell in mini_q:  # check if any of the mini q cells are already existing in q; if so, remake
                        if tmp_cell in drawing_q:
                            self_hit = True
                            break
                    begin_direction = CD(begin_direction)
                    begin_cell = mini_q[-1]
                    drawing_q.extend(mini_q)

                    if begin_cell.is_edge_cell():  # if the last cell queued is an edge cell, set edge_hit to true
                        edge_hit = True

            if len(drawing_q) >= 100 and not river_hit and not self_hit:
                valid_river = True

        if valid_river:
            for cell in drawing_q:
                cell.is_highway = True
                draw_cell_rect(map_surface, cell.get_color(), cell.pixel_x, cell.pixel_y, DEFAULT_BORDER_COLOR, 1)
                MAIN_SCREEN.blit(map_surface, (0, 0))
                pygame.display.update()

    return


def draw_blocked_cells_on_grid(map_surface, grid, num_blocked):

    blocked_cells_drawn = 0
    while blocked_cells_drawn != num_blocked:
        random_cell = grid[randint(0, GRID_BLOCKS_TALL-1)][randint(0, GRID_BLOCKS_WIDE-1)]
        if not random_cell.is_highway or not random_cell.c_type:
            random_cell.c_type = 0  # update to blocked cell
            blocked_cells_drawn += 1
            draw_cell_rect(map_surface, random_cell.get_color(), random_cell.pixel_x, random_cell.pixel_y, DEFAULT_BORDER_COLOR, 1)

    MAIN_SCREEN.blit(map_surface, (0, 0))
    pygame.display.update()
    return


def draw_get_start_and_goal(grid, map_base):

    clear_start_goal_nodes(grid)
    tmp_map_surface = map_base.copy()

    MAIN_SCREEN.blit(tmp_map_surface, (0,0))
    pygame.display.update()

    while True:  # first determine the start cell
        if random() < 0.5:
            start_row = choice([randint(0, 19), randint(100, 119)])  # rows: top 20 or bottom 20
            start_col = randint(0, GRID_BLOCKS_WIDE-1)
        else:
            start_row = randint(0, GRID_BLOCKS_TALL-1)
            start_col = choice([randint(0, 19), randint(139, 159)])  # cols: left 20 or right 20

        start_node = grid[start_row][start_col]
        if start_node.c_type != 0:  # if this cell is not blocked, break out of the while loop
            break

    while True:  # then determine goal cell and test the distance
        if random() < 0.5:
            goal_row = choice([randint(0, 19), randint(100, 119)])  # rows: top 20 or bottom 20
            goal_col = randint(0, GRID_BLOCKS_WIDE-1)
        else:
            goal_row = randint(0, GRID_BLOCKS_TALL-1)
            goal_col = choice([randint(0, 19), randint(139, 159)])  # cols: left 20 or right 20

        goal_node = grid[goal_row][goal_col]
        distance = E_dist(start_node, goal_node)
        if goal_node.c_type != 0 and distance >= 100:  # if this cell is not blocked, test to see if it's euclidean distance >= 100

            start_node.is_start = True
            goal_node.is_goal = True

            draw_cell_rect(tmp_map_surface, start_node.get_color(), start_node.pixel_x, start_node.pixel_y, DEFAULT_BORDER_COLOR, 1)
            draw_cell_rect(tmp_map_surface, goal_node.get_color(), goal_node.pixel_x, goal_node.pixel_y, DEFAULT_BORDER_COLOR, 1)

            MAIN_SCREEN.blit(tmp_map_surface, (0,0))
            pygame.display.update()

            break

    return start_node, goal_node, tmp_map_surface


def draw_cell_rect(map_surface, inner_color, pix_x, pix_y, border_color = DEFAULT_BORDER_COLOR, border_thickness = 0):

    if border_thickness <= 0:  # if not border needed
        pygame.draw.rect(map_surface, inner_color, (pix_x, pix_y, SCALE, SCALE), 0)
    else:
        pygame.draw.rect(map_surface, border_color, (pix_x, pix_y, SCALE, SCALE), border_thickness)
        pygame.draw.rect(map_surface, inner_color, (pix_x + border_thickness,
                                                    pix_y + border_thickness,
                                                    SCALE - border_thickness,
                                                    SCALE - border_thickness), 0)

    return


def display_info(cell):

    l_bgc = cell.get_color()
    if l_bgc == WHITE or l_bgc == GREEN or l_bgc == RED:
        l_ftc = BLACK
    else:
        l_ftc = WHITE

    if l_bgc == WHITE:
        l_bgc = LIGHT_GRAY

    text = '{} | h={} g={} f={} | ROW{}, COL{}'.format(cell.get_type_string(), round(cell.h_value,5), round(cell.g_value,5),
                                                       round(cell.h_value+cell.g_value,5), cell.row+1, cell.col+1)
    label_width, label_height = FONT.size(text)

    if cell.row < GRID_BLOCKS_TALL/2:
        y_offset = SCALE
    else:
        y_offset = -label_height

    if cell.col < GRID_BLOCKS_WIDE/2:
        x_offset = SCALE
    else:
        x_offset = -label_width

    label = FONT.render(text, 1, l_ftc, l_bgc)
    MAIN_SCREEN.blit(label, (cell.pixel_x+x_offset, cell.pixel_y+y_offset))
    pygame.display.update()

    return










if __name__ == '__main__':
    main()
