from random import choice, randint, random
from win32api import GetSystemMetrics
import pygame
import math
from datetime import datetime
from utils.the_david_brian_heap import DavidsAndBriansHeapForCellPriorityWithAReallyLongName as DABHFCPWARLN
from utils.colors import *
import sys
from utils.helper_defs import round_down_to_multiple as RDTM, euclidean_dist as E_dist, manhattan_dist as M_dist, \
                              change_direction as CD, chebyshev_dist as C_dist, our_inadmissible_dist as In_dist, \
                              our_admissible_dist as A_dist

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
FONT_SIZE = 19
FONT = None
INTERNAL_MAP = []  # internal map (list of lists)
EXTERNAL_MAP_BASE = None  # map visual with no goals
EXTERNAL_MAP_FULL = None  # map visual with goals and all
START_NODE = None
GOAL_NODE = None
MAIN_SCREEN = None
GRAPH = None

MEM_START = 0


UCS = {'UCS': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []}}

A_STAR = {'A_STAR_CHEB': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
          'A_STAR_MAN': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
          'A_STAR_EUC': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
          'A_STAR_IN': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
          'A_STAR_A': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []}}

A_STAR_W1 = {'A_STAR_W1_CHEB': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
             'A_STAR_W1_MAN': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
             'A_STAR_W1_EUC': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
             'A_STAR_W1_IN': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
             'A_STAR_W1_A': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []}}

A_STAR_W2 = {'A_STAR_W2_CHEB': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
             'A_STAR_W2_MAN': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
             'A_STAR_W2_EUC': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
             'A_STAR_W2_IN': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []},
             'A_STAR_W2_A': {'RUNTIME': [], 'MEM_USED': [], 'LENGTH_PATH': [], 'NODES_EXPANDED': []}}












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

    MAIN_SCREEN.fill(WHITE)
    pygame.draw.rect(MAIN_SCREEN, LIGHT_GRAY, (MAP_WIDTH, 0, INTERFACE_WIDTH, INTERFACE_HEIGHT), 0)  # BORDER
    pygame.draw.rect(MAIN_SCREEN, LIGHT_GRAY, (MAP_WIDTH + INTERFACE_PADDING, INTERFACE_PADDING,
                                               INTERFACE_WIDTH - 2 * INTERFACE_PADDING,
                                               INTERFACE_HEIGHT - 2 * INTERFACE_PADDING), 0)  # INNER

    pygame.display.update()
    return


def main():
    global FONT, MAIN_SCREEN, INTERNAL_MAP, RUNTIME, MEM_START

    pygame.init()
    MAIN_SCREEN = pygame.display.set_mode((SYSTEM_WIDTH, SYSTEM_HEIGHT), pygame.FULLSCREEN)
    icon = pygame.image.load('robot_icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('CS440 Assignment 1')
    FONT = pygame.font.SysFont("monospace", FONT_SIZE)

    load_user_interface()

    for _ in range(0,5):
        generate_a_map()

        for _ in range(0,10):
            draw_get_start_and_goal()

    wtf = [UCS, A_STAR, A_STAR_W1, A_STAR_W2]

    for w in wtf:
        for search_type, results in w.items():
            print('\n',search_type,'-------------------------------------------------')
            # avg_runtime = sum(w[search_type]['RUNTIME']) / 1
            # avg_mem = sum(w[search_type]['MEM_USED']) / 1
            # avg_length = sum(w[search_type]['LENGTH_PATH']) / 1
            # avg_nodes_exp = sum(w[search_type]['NODES_EXPANDED']) / 1


            avg_runtime = sum(w[search_type]['RUNTIME'])/len(w[search_type]['RUNTIME'])
            avg_mem =  sum(w[search_type]['MEM_USED'])/len(w[search_type]['MEM_USED'])
            avg_length =  sum(w[search_type]['LENGTH_PATH'])/len(w[search_type]['LENGTH_PATH'])
            avg_nodes_exp = sum(w[search_type]['NODES_EXPANDED']) / len(w[search_type]['NODES_EXPANDED'])

            print('PRECHECK: SEARCH TYPE: {}, [{},{},{},{}]'.format(search_type,len(w[search_type]['RUNTIME']),
                                                                                len(w[search_type]['MEM_USED']),
                                                                                len(w[search_type]['LENGTH_PATH']),
                                                                                len(w[search_type]['NODES_EXPANDED'])
                                                                    ))
            print('\tAVG RUNTIME: {}\n\tAVG MEMORY: {}\n\tAVG LENGTH: {}\n\tAVG NODES EXPANDED: {}'.format(avg_runtime, avg_mem, avg_length, avg_nodes_exp))


    exit()




    pygame.display.update()
    previous_highlighted_cell = normal_color = highlighted_cell = None
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_c:  # clear labels, keep map and start/goal
                    MAIN_SCREEN.blit(EXTERNAL_MAP_FULL, (0, 0))
                    pygame.display.update()
                if e.key == pygame.K_n:  # new map
                    generate_a_map()
                    pygame.display.update()
                if e.key == pygame.K_g:  # new start/goal cells
                    draw_get_start_and_goal()
                    pygame.display.update()
                if e.key == pygame.K_a:  # rerun a* normal
                    a_star()
                    pygame.display.update()
                if e.key == pygame.K_b:  # rerun a* normal with search space showing
                    a_star(show_search_space=True)
                    pygame.display.update()
                if e.key == pygame.K_u:  # rerun UCS
                    uniform_cost_search()
                    pygame.display.update()
                if e.key == pygame.K_w:  # rerun weighted A*
                    a_star_weighted(2)
                    pygame.display.update()
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # if left mouse button clicked
                m_pos = pygame.mouse.get_pos()
                pix_x = m_pos[0]
                pix_y = m_pos[1]

                if pix_x < MAP_WIDTH:  # means clicked within the map and not the interface
                    c_pix_x = RDTM(pix_x, SCALE)
                    c_pix_y = RDTM(pix_y, SCALE)

                    row = int(c_pix_y / SCALE)
                    col = int(c_pix_x / SCALE)
                    clicked_cell = INTERNAL_MAP[row][col]
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

                    if highlighted_cell != INTERNAL_MAP[row][col]:
                        highlighted_cell = INTERNAL_MAP[row][col]

                        if previous_highlighted_cell:
                            if previous_highlighted_cell is not highlighted_cell:
                                draw_cell_rect(MAIN_SCREEN, normal_color, previous_highlighted_cell.pixel_x,
                                               previous_highlighted_cell.pixel_y, DEFAULT_BORDER_COLOR, 1)
                                pygame.display.update()

                        normal_color = MAIN_SCREEN.get_at((highlighted_cell.pixel_x + 5, highlighted_cell.pixel_y + 5))
                        draw_cell_rect(MAIN_SCREEN, YELLOW, highlighted_cell.pixel_x,
                                       highlighted_cell.pixel_y, DEFAULT_BORDER_COLOR, 1)
                        pygame.display.update()
                        previous_highlighted_cell = INTERNAL_MAP[row][col]

                else:
                    pass

    return


def generate_a_map():
    global INTERNAL_MAP, EXTERNAL_MAP_BASE, EXTERNAL_MAP_FULL

    map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA, 32)
    map_surface = map_surface.convert_alpha()

    draw_init_grid(map_surface)
    draw_htt_areas(map_surface, NUMBER_OF_HTT_AREAS)
    draw_rivers(map_surface, NUMBER_OF_RIVERS)
    draw_blocked_cells(map_surface, NUMBER_OF_BLOCKED_CELLS)

    EXTERNAL_MAP_BASE = map_surface.copy()


    return


def draw_init_grid(map_surface):
    global INTERNAL_MAP
    grid_map = []

    for vertical_pixel in range(0, MAP_HEIGHT, SCALE):
        temp_row = []
        for horizontal_pixel in range(0, MAP_WIDTH, SCALE):
            temp_cell = Cell(horizontal_pixel, vertical_pixel, vertical_pixel / SCALE, horizontal_pixel / SCALE, 1)
            temp_row.append(temp_cell)
            draw_cell_rect(map_surface, temp_cell.get_color(), horizontal_pixel, vertical_pixel, DEFAULT_BORDER_COLOR, 1)
        grid_map.append(temp_row)

    INTERNAL_MAP = grid_map
    MAIN_SCREEN.blit(map_surface, (0, 0))
    pygame.display.update()
    return


def draw_htt_areas(map_surface, num_htt_areas):
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
                        tmp_cell = INTERNAL_MAP[tmp_row][tmp_col]
                        tmp_cell.c_type = 2  # set to HTT
                        draw_cell_rect(map_surface, tmp_cell.get_color(),
                                       tmp_cell.pixel_x, tmp_cell.pixel_y, DEFAULT_BORDER_COLOR, 1)

        MAIN_SCREEN.blit(map_surface, (0, 0))
        pygame.display.update()

    return


def draw_rivers(map_surface, num_rivers):

    for r_num in range(num_rivers):
        valid_river = False
        drawing_q = []

        while not valid_river:
            # if not valid river...
            drawing_q = []  # reset the drawing queue
            river_origin_cell = get_riverless_edge_cell()  # get a new river origin not on a river
            current_direction = river_start_direction(river_origin_cell)  # get direction to begin in
            drawing_q.append(river_origin_cell)
            edge_hit = False
            river_hit = False
            self_hit = False

            begin_direction = current_direction
            begin_cell = river_origin_cell

            while not edge_hit:
                mini_q = twenty_steps_in_direction(begin_cell, begin_direction)
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

            # first_cell = drawing_q[0]
            # draw_cell_rect(map_surface, GREEN, first_cell.pixel_x, first_cell.pixel_y, LIGHT_GRAY, 1)
            # last_cell = drawing_q[-1]
            # draw_cell_rect(map_surface, RED, last_cell.pixel_x, last_cell.pixel_y, LIGHT_GRAY, 1)

    return


def draw_blocked_cells(map_surface, num_blocked):

    blocked_cells_drawn = 0
    while blocked_cells_drawn != num_blocked:
        random_cell = INTERNAL_MAP[randint(0, GRID_BLOCKS_TALL-1)][randint(0, GRID_BLOCKS_WIDE-1)]
        if not random_cell.is_highway or not random_cell.c_type:
            random_cell.c_type = 0  # update to blocked cell
            blocked_cells_drawn += 1
            draw_cell_rect(map_surface, random_cell.get_color(), random_cell.pixel_x, random_cell.pixel_y, DEFAULT_BORDER_COLOR, 1)

    MAIN_SCREEN.blit(map_surface, (0, 0))
    pygame.display.update()
    return


def draw_get_start_and_goal():

    global EXTERNAL_MAP_FULL, START_NODE, GOAL_NODE

    tmp_map_surface = EXTERNAL_MAP_BASE.copy()

    start_row = start_col = goal_row = goal_col = color = None

    if START_NODE:  # if start node already exists, clear it
        START_NODE.is_start = False

    if GOAL_NODE:  # if goal node already exists, clear it
        GOAL_NODE.is_goal = False

    MAIN_SCREEN.blit(tmp_map_surface, (0,0))
    pygame.display.update()

    while True:  # first determine the start cell
        if random() < 0.5:
            start_row = choice([randint(0, 19), randint(100, 119)])  # rows: top 20 or bottom 20
            start_col = randint(0, GRID_BLOCKS_WIDE-1)
        else:
            start_row = randint(0, GRID_BLOCKS_TALL-1)
            start_col = choice([randint(0, 19), randint(139, 159)])  # cols: left 20 or right 20

        START_NODE = INTERNAL_MAP[start_row][start_col]
        if START_NODE.c_type != 0:  # if this cell is not blocked, break out of the while loop
            break

    while True:  # then determine goal cell and test the distance
        if random() < 0.5:
            goal_row = choice([randint(0, 19), randint(100, 119)])  # rows: top 20 or bottom 20
            goal_col = randint(0, GRID_BLOCKS_WIDE-1)
        else:
            goal_row = randint(0, GRID_BLOCKS_TALL-1)
            goal_col = choice([randint(0, 19), randint(139, 159)])  # cols: left 20 or right 20

        GOAL_NODE = INTERNAL_MAP[goal_row][goal_col]
        distance = E_dist(START_NODE, GOAL_NODE)
        if GOAL_NODE.c_type != 0 and distance >= 100:  # if this cell is not blocked, test to see if it's euclidean distance >= 100

            START_NODE.is_start = True
            GOAL_NODE.is_goal = True

            # code snippet below draws a halo around start node and goal node (comes before goal/start drawing so its underneath them)
            # tmp_rect = pygame.Surface((SCALE * 7, SCALE * 7))
            # tmp_rect.set_alpha(100)
            # tmp_rect.fill(YELLOW)
            # tmp_map_surface.blit(tmp_rect, (START_NODE.pixel_x - 3 * SCALE, START_NODE.pixel_y - 3 * SCALE))
            # tmp_map_surface.blit(tmp_rect, (GOAL_NODE.pixel_x - 3 * SCALE, GOAL_NODE.pixel_y - 3 * SCALE))
            # -------

            draw_cell_rect(tmp_map_surface, START_NODE.get_color(), START_NODE.pixel_x, START_NODE.pixel_y, DEFAULT_BORDER_COLOR, 1)
            draw_cell_rect(tmp_map_surface, GOAL_NODE.get_color(), GOAL_NODE.pixel_x, GOAL_NODE.pixel_y, DEFAULT_BORDER_COLOR, 1)

            MAIN_SCREEN.blit(tmp_map_surface, (0,0))
            pygame.display.update()

            break

    EXTERNAL_MAP_FULL = tmp_map_surface.copy()

    # AFTER ESTABLISHING START/GOALS, SET THE G, H, AND F VALUES AND SET THE NEIGHBORS OF EACH ONE AND SOLVE PATH
    s = datetime.now()
    set_cell_values()
    # print('set values: {}'.format(datetime.now() - s))

    s = datetime.now()
    set_cell_neighbors()
    # print('set neighbors: {}'.format(datetime.now() - s))


    heuristics = {0: C_dist, 1: M_dist, 2: E_dist, 3: In_dist, 4: A_dist}
    h_string = {0: 'CHEB', 1: 'MAN', 2: 'EUC', 3: 'IN', 4: 'A'}

    for x in range(0,5):
        uniform_cost_search(heuristics[x], '', 0, 'UCS')

        a_star(heuristics[x], h_string[x], 1, 'A_STAR')

        a_star_weighted(heuristics[x], h_string[x], 1.25, 'A_STAR_W1')

        a_star_weighted(heuristics[x], h_string[x], 2, 'A_STAR_W2')


    return


def twenty_steps_in_direction(cell, direction):  # returns empty list if invalid river, otherwise returns mini q

    mini_q = []
    current_row = cell.row
    current_col = cell.col

    if direction == 'Up':
        tmp_range = range(current_row, current_row - 20, -1)  # iterates from current cell's row to 20 rows above it
        vertical = True
        sign = -1
    elif direction == 'Down':
        tmp_range = range(current_row, current_row + 20, 1)  # iterates from current cell's row to 20 rows below it
        vertical = True
        sign = 1
    elif direction == 'Left':
        tmp_range = range(current_col, current_col - 20, -1)  # iterates from current cell's col to 20 rows left of it
        vertical = False
        sign = -1
    elif direction == 'Right':
        tmp_range = range(current_col, current_col + 20, 1)  # iterates from current cell's col to 20 rows right of it
        vertical = False
        sign = 1
    else:
        print('NOT SUPPOSE TO GET HERE.')
        return

    for new in tmp_range:
        if vertical:
            next_cell = INTERNAL_MAP[new + sign*1][current_col]
        else:
            next_cell = INTERNAL_MAP[current_row][new + sign * 1]

        if next_cell.is_highway:
            return []

        if next_cell.is_edge_cell():  # if prematurely hits edge cell, add that edge cell to mini q and return
            mini_q.append(next_cell)
            return mini_q
        else:
            mini_q.append(next_cell)  # otherwise continue adding next cells to q

    return mini_q  # if not failed, then return list which will guarantee to have at least one cell in it


def river_start_direction(cell):

    if cell.col == 0: return 'Right'
    elif cell.col == GRID_BLOCKS_WIDE - 1: return 'Left'
    elif cell.row == 0: return 'Down'
    elif cell.row == GRID_BLOCKS_TALL - 1: return 'Up'
    else: return 'DIRECTIONAL ERROR OCCURRED.'


def get_riverless_edge_cell():  # returns a cell object on the edge that is not occupied by a river
    # random cell on top-most row excluding corners
    rand_top_edge = [0, randint(1, GRID_BLOCKS_WIDE - 2)]
    # random cell on bottom-most row excluding corners
    rand_bot_edge = [GRID_BLOCKS_TALL - 1, randint(1, GRID_BLOCKS_WIDE - 2)]

    # random cell on left-most column excluding corners
    rand_left_edge = [randint(1, GRID_BLOCKS_TALL - 2), 0]
    # random cell on right-most column excluding corners
    rand_right_edge = [randint(1, GRID_BLOCKS_TALL - 2), GRID_BLOCKS_WIDE - 1]

    # now choose from the above four:
    rand_row_col = choice([rand_top_edge, rand_bot_edge, rand_left_edge, rand_right_edge])

    temp_cell = INTERNAL_MAP[rand_row_col[0]][rand_row_col[1]]

    if temp_cell.is_highway:
        return get_riverless_edge_cell()
    else:
        return temp_cell


def print_grid_map():
    for row in INTERNAL_MAP:
        for cell in row:
            g_s_indicator = highway_indicator = ''
            if cell.is_start:
                g_s_indicator = 'START'
            if cell.is_goal:
                g_s_indicator = 'GOAL'
            if cell.is_highway:
                highway_indicator = 'HIGHWAY'
            print('[{}][{}]-{}-{}-{}'.format(cell.row, cell.col, cell.c_type, highway_indicator, g_s_indicator), end='  |  ')
        print('')

    return


def print_neighbors():

    for row in INTERNAL_MAP:
        for cell in row:
            print('R{}C{}: {}'.format(cell.row, cell.col, [(c.row, c.col) for c in cell.neighbors]))


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


def set_cell_values():
    for row in INTERNAL_MAP:
        for cell in row:
            if cell.c_type == 0:  # if blocked cell, you can't get to it, and you can't use it to get anywhere
                cell.h_value = 99999999
                cell.g_value = 99999999
            else:
                cell.h_value = C_dist(cell, GOAL_NODE)  # HEURISTIC VALUE (EUCLIDEAN, MANHATTAN, ETC.)
                cell.g_value = 99999999  # THE COST FROM START TO N FOUND SO FAR
    return


def set_cell_neighbors():
    for r in INTERNAL_MAP:
        for cell in r:
            tmp_neighbors = []
            for row in range(cell.row-1, cell.row+2):
                if row < 0:
                    continue
                for col in range(cell.col-1, cell.col+2):
                    if col < 0:
                        continue

                    try:
                        neighbor = INTERNAL_MAP[row][col]
                        if neighbor is not cell and neighbor.c_type != 0:
                            tmp_neighbors.append(neighbor)
                    except IndexError:
                        pass
            cell.neighbors.extend(tmp_neighbors)
    return


def draw_instructions(screen, font):
    instructions = 'NOTE: Click a cell for details. Press \'c\' to clear all labels. Press \'n\' for new map.'.upper()
    label_width, label_height = font.size(instructions)
    label = font.render(instructions, 1, BLACK, DARK_CYAN)
    screen.blit(label, ((SYSTEM_WIDTH-label_width)/2, 0))
    pygame.display.update()


def display_info(cell):

    l_bgc = cell.get_color()
    if l_bgc == WHITE or l_bgc == GREEN or l_bgc == RED:
        l_ftc = BLACK
    else:
        l_ftc = WHITE

    text = '{} | h={} g={} f={} | ROW{}, COL{}'.format(cell.get_type_string(), cell.h_value, cell.g_value,
                                                       cell.h_value+cell.g_value, cell.row+1, cell.col+1)
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


def a_star(heuristic_func, h_string, weight, search_type):

    global LENGTH_PATH, NODES_EXPANDED, UCS, A_STAR, A_STAR_W1, A_STAR_W2
    mem_track = []
    mem_track.append(memory())

    runtime_start = datetime.now()

    reset_cells()

    if weight == 0:
        path_color = YELLOW
        # print('\nUNIFORM COST SEARCH - - - -')
    elif weight == 1:
        path_color = GREEN
        # print('\nA* NORMAL - - - -')
    else:
        path_color = CYAN
        # print('\nA* WEIGHTED (w={}) - - - -'.format(weight))



    START_NODE.g_value = 0
    START_NODE.parent = None
    fringe = DABHFCPWARLN()
    fringe.insert(START_NODE, START_NODE.g_value + heuristic_func(START_NODE, GOAL_NODE) * weight)
    START_NODE.in_fringe = True
    path_solution = []

    mem_track.append(memory())


    while not fringe.is_empty():

        current_cell = fringe.pop()


        # snippet colors in search process.
        # if show_search_space and current_cell.c_type == 1 and not current_cell.is_highway:
        #     current_color = map_color_gradient(gradient_color_1, gradient_color_2, current_cell)
        #     tmp_rect = pygame.Surface((SCALE-1, SCALE-1))
        #     tmp_rect.set_alpha(100)
        #     tmp_rect.fill(current_color)
        #     MAIN_SCREEN.blit(tmp_rect, (current_cell.pixel_x+1, current_cell.pixel_y+1))
        #     pygame.display.update()
        # --------


        if current_cell is GOAL_NODE:  # goal found
            mem_track.append(memory())
            previous = GOAL_NODE.parent
            while previous.parent:
                path_solution.append(previous)
                previous = previous.parent

            path_solution = path_solution[::-1]
            #
            # for cell in path_solution:
            #     current_color = map_color_gradient(gradient_color_1, gradient_color_2, cell)
            #     tmp_sq = pygame.Surface((SCALE - 1, SCALE - 1))
            #     # tmp_sq.set_alpha(175)  # opacity of path drawn. default = 175
            #     tmp_sq.fill(current_color)
            #     MAIN_SCREEN.blit(tmp_sq, (cell.pixel_x + 1, cell.pixel_y + 1))
            #     pygame.display.update()

            # memory_used_in_bytes = sum(mem_track)/len(mem_track)
            open_list = [cell.expanded_already for row in INTERNAL_MAP for cell in row]
            memory_used_in_bytes = sys.getsizeof(fringe) + sum([sys.getsizeof(cell) for cell in open_list])
            runtime_in_ms = (datetime.now() - runtime_start).microseconds / 1000
            path_length = GOAL_NODE.g_value
            nodes_expanded = sum(open_list)

            if search_type == 'UCS':

                UCS['UCS']['RUNTIME'].append(runtime_in_ms)
                UCS['UCS']['MEM_USED'].append(memory_used_in_bytes)
                UCS['UCS']['LENGTH_PATH'].append(path_length)
                UCS['UCS']['NODES_EXPANDED'].append(nodes_expanded)

            elif search_type == 'A_STAR':
                A_STAR['{}_{}'.format(search_type, h_string)]['RUNTIME'].append(runtime_in_ms)
                A_STAR['{}_{}'.format(search_type, h_string)]['MEM_USED'].append(memory_used_in_bytes)
                A_STAR['{}_{}'.format(search_type, h_string)]['LENGTH_PATH'].append(path_length)
                A_STAR['{}_{}'.format(search_type, h_string)]['NODES_EXPANDED'].append(nodes_expanded)

            elif search_type == 'A_STAR_W1':
                A_STAR_W1['{}_{}'.format(search_type, h_string)]['RUNTIME'].append(runtime_in_ms)
                A_STAR_W1['{}_{}'.format(search_type, h_string)]['MEM_USED'].append(memory_used_in_bytes)
                A_STAR_W1['{}_{}'.format(search_type, h_string)]['LENGTH_PATH'].append(path_length)
                A_STAR_W1['{}_{}'.format(search_type, h_string)]['NODES_EXPANDED'].append(nodes_expanded)

            elif search_type == 'A_STAR_W2':
                A_STAR_W2['{}_{}'.format(search_type, h_string)]['RUNTIME'].append(runtime_in_ms)
                A_STAR_W2['{}_{}'.format(search_type, h_string)]['MEM_USED'].append(memory_used_in_bytes)
                A_STAR_W2['{}_{}'.format(search_type, h_string)]['LENGTH_PATH'].append(path_length)
                A_STAR_W2['{}_{}'.format(search_type, h_string)]['NODES_EXPANDED'].append(nodes_expanded)



            return

        current_cell.expanded_already = True
        for neighbor in current_cell.neighbors:

            if not neighbor.expanded_already:
                if not neighbor.in_fringe:
                    neighbor.g_value = 99999999
                    neighbor.parent = None
                if current_cell.g_value + calc_g_value(current_cell, neighbor) < neighbor.g_value:
                    neighbor.g_value = current_cell.g_value + calc_g_value(current_cell, neighbor)
                    neighbor.parent = current_cell
                    if neighbor.in_fringe:
                        fringe.remove(neighbor)
                        neighbor.in_fringe = False
                    fringe.insert(neighbor, neighbor.g_value + heuristic_func(neighbor, GOAL_NODE) * weight)
                    neighbor.in_fringe = True

    print('No Path to Goal Found.')



    return


def a_star_weighted(heuristic_func, h_string, weight, search_type):
    a_star(heuristic_func, h_string, weight, search_type)
    return


def uniform_cost_search(heuristic_func, h_string, weight, search_type):
    a_star(heuristic_func, h_string, weight, search_type)
    return


def calc_g_value(current, next):
    tmp_value = 0

    if (current.row != next.row) and (current.col != next.col):  # we are moving diagonally
        if current.c_type == 2 and next.c_type == 2:  # both are HTT
            tmp_value = math.sqrt(8)
        elif current.c_type == 1 and next.c_type == 1:  # both are normal
            tmp_value = math.sqrt(2)
        else:
            tmp_value = (math.sqrt(2) + math.sqrt(8)) / 2

    else:  # we are moving horizontally OR vertically, not both
        if current.c_type == 2 and next.c_type == 2:  # both are HTT
            tmp_value = 2
        elif current.c_type == 1 and next.c_type == 1:  # both are normal
            tmp_value = 1
        else:
            tmp_value = 1.5

    # now we check if both cells are highways
    if current.is_highway and next.is_highway:
        return tmp_value * 0.25

    return tmp_value


def memory():
    import os
    from wmi import WMI
    w = WMI('.')
    result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % os.getpid())
    return int(result[0].WorkingSet)


def map_color_gradient(c1, c2, current_cell):
    # uses distance to goal from current cell to get current color

    percentage = (START_NODE.h_value-current_cell.h_value)/START_NODE.h_value

    if percentage > 1:
        percentage = 1
    elif percentage < 0:
        percentage = 0


    r = c2[0] - c1[0]
    g = c2[1] - c1[1]
    b = c2[2] - c1[2]

    return (int(percentage * r) + c1[0], int(percentage * g) + c1[1], int(percentage * b) + c1[2])


def reset_cells():

    set_cell_values()

    for row in INTERNAL_MAP:
        for cell in row:
            cell.parent = None
            cell.in_fringe = False
            cell.expanded_already = False


if __name__ == '__main__':
    main()