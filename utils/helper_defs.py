import math
from datetime import datetime
from random import choice, randint
from random import random


def memory():
    import os
    from wmi import WMI
    w = WMI('.')
    result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % os.getpid())
    return int(result[0].WorkingSet)


def reset_cells_in_grid(grid):
    for row in grid:
        for cell in row:
            cell.parent = None
            cell.in_fringe = False
            cell.expanded_already = False


def set_cell_values(grid, goal_node, heuristic):
    for row in grid:
        for cell in row:
            if cell.c_type == 0:  # if blocked cell, you can't get to it, and you can't use it to get anywhere
                cell.h_value = 99999999.0
                cell.g_value = 99999999.0
            elif heuristic:
                cell.h_value = heuristic(cell, goal_node)  # HEURISTIC VALUE (EUCLIDEAN, MANHATTAN, ETC.)
                cell.g_value = 99999999.0  # THE COST FROM START TO N FOUND SO FAR
            else:
                cell.h_value = 0.0
                cell.g_value = 99999999.0
    return


def set_cell_neighbors(grid):
    for r in grid:
        for cell in r:
            tmp_neighbors = []
            for row in range(cell.row - 1, cell.row + 2):
                if row < 0:
                    continue
                for col in range(cell.col - 1, cell.col + 2):
                    if col < 0:
                        continue

                    try:
                        neighbor = grid[row][col]
                        if neighbor is not cell and neighbor.c_type != 0:
                            tmp_neighbors.append(neighbor)
                    except IndexError:
                        pass
            cell.neighbors.extend(tmp_neighbors)
    return


def calc_g_value(current_cell, next_cell):
    tmp_value = 0

    if (current_cell.row != next_cell.row) and (current_cell.col != next_cell.col):  # we are moving diagonally
        if current_cell.c_type == 2 and next_cell.c_type == 2:  # both are HTT
            tmp_value = math.sqrt(8)
        elif current_cell.c_type == 1 and next_cell.c_type == 1:  # both are normal
            tmp_value = math.sqrt(2)
        else:
            tmp_value = (math.sqrt(2) + math.sqrt(8)) / 2

    else:  # we are moving horizontally OR vertically, not both
        if current_cell.c_type == 2 and next_cell.c_type == 2:  # both are HTT
            tmp_value = 2
        elif current_cell.c_type == 1 and next_cell.c_type == 1:  # both are normal
            tmp_value = 1
        else:
            tmp_value = 1.5

    # now we check if both cells are highways
    if current_cell.is_highway and next_cell.is_highway:
        return tmp_value * 0.25

    return tmp_value


def twenty_steps_in_direction(grid, cell, direction):  # returns empty list if invalid river, otherwise returns mini q

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
            next_cell = grid[new + sign * 1][current_col]
        else:
            next_cell = grid[current_row][new + sign * 1]

        if next_cell.is_highway:
            return []

        if next_cell.is_edge_cell():  # if prematurely hits edge cell, add that edge cell to mini q and return
            mini_q.append(next_cell)
            return mini_q
        else:
            mini_q.append(next_cell)  # otherwise continue adding next cells to q

    return mini_q  # if not failed, then return list which will guarantee to have at least one cell in it


def river_start_direction(cell):
    if cell.col == 0:
        return 'Right'
    elif cell.col == 159:
        return 'Left'
    elif cell.row == 0:
        return 'Down'
    elif cell.row == 119:
        return 'Up'
    else:
        return 'DIRECTIONAL ERROR OCCURRED.'


def clear_start_goal_nodes(grid):
    for row in grid:
        for cell in row:
            cell.is_start = False
            cell.is_goal = False


def get_riverless_edge_cell(grid):  # returns a cell object on the edge that is not occupied by a river
    # random cell on top-most row excluding corners
    rand_top_edge = [0, randint(1, 158)]
    # random cell on bottom-most row excluding corners
    rand_bot_edge = [119, randint(1, 158)]

    # random cell on left-most column excluding corners
    rand_left_edge = [randint(1, 118), 0]
    # random cell on right-most column excluding corners
    rand_right_edge = [randint(1, 118), 159]

    # now choose from the above four:
    rand_row_col = choice([rand_top_edge, rand_bot_edge, rand_left_edge, rand_right_edge])

    temp_cell = grid[rand_row_col[0]][rand_row_col[1]]

    if temp_cell.is_highway:
        return get_riverless_edge_cell(grid)
    else:
        return temp_cell


def print_grid_map(grid):
    for row in grid:
        for cell in row:
            g_s_indicator = highway_indicator = ''
            if cell.is_start:
                g_s_indicator = 'START'
            if cell.is_goal:
                g_s_indicator = 'GOAL'
            if cell.is_highway:
                highway_indicator = 'HIGHWAY'
            print('[{}][{}]-{}-{}-{}'.format(cell.row, cell.col, cell.c_type, highway_indicator, g_s_indicator),
                  end='  |  ')
        print('')

    return


def print_all_neighbors_in_grid(grid):
    for row in grid:
        for cell in row:
            print('R{}C{}: {}'.format(cell.row, cell.col, [(c.row, c.col) for c in cell.neighbors]))


def save_the_map(grid, start, goal, htt_coords):
    f = open('Generated Map - {}.txt'.format(datetime.now().strftime("%m-%d-%Y %I %M %S %p")), 'a')
    f.write('{},{}\n'.format(start.row, start.col))
    f.write('{},{}\n'.format(goal.row, goal.col))
    for region in htt_coords:
        f.write('{},{}\n'.format(region[1], region[0]))
    for each_row in grid:
        for each_cell in each_row:

            if each_cell.is_highway:
                if each_cell.c_type == 1:
                    cell_type = 'a'
                elif each_cell.c_type == 2:
                    cell_type = 'b'
            elif not each_cell.is_highway:
                cell_type = each_cell.c_type
            else:
                cell_type = '$'

            f.write('{}'.format(cell_type))
        f.write('\n')
    f.close()


def round_down_to_multiple(num, multiple):
    return num - (num % multiple)


def euclidean_dist(start_c, goal_c):
    x1 = start_c.col
    y1 = start_c.row
    x2 = goal_c.col
    y2 = goal_c.row
    return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2))


def manhattan_dist(start_c, goal_c):
    x1 = start_c.col
    y1 = start_c.row
    x2 = goal_c.col
    y2 = goal_c.row
    return (abs(x1 - x2) + abs(y1 - y2))


def chebyshev_dist(start_c, goal_c):
    x1 = start_c.col
    y1 = start_c.row
    x2 = goal_c.col
    y2 = goal_c.row
    return max(abs(x1 - x2), abs(y1 - y2))


def our_inadmissible_dist(start_c, goal_c):
    return (manhattan_dist(start_c, goal_c) + euclidean_dist(start_c, goal_c)) / 2


def our_admissible_dist(start_c, goal_c):
    return manhattan_dist(start_c, goal_c) / 4


def change_direction(current_dir):
    if current_dir == 'Left':
        rand = random()
        if rand <= .2:
            return 'Up'
        elif rand >= .8:
            return 'Down'
        else:
            return current_dir

    if current_dir == 'Right':
        rand = random()
        if rand <= .2:
            return 'Up'
        elif rand >= .8:
            return 'Down'
        else:
            return current_dir

    if current_dir == 'Up':
        rand = random()
        if rand <= .2:
            return 'Left'
        elif rand >= .8:
            return 'Right'
        else:
            return current_dir

    if current_dir == 'Down':
        rand = random()
        if rand <= .2:
            return 'Left'
        elif rand >= .8:
            return 'Right'
        else:
            return current_dir


def map_color_gradient(c1, c2, current_cell, start):
    # uses distance to goal from current cell to get current color

    percentage = (start.h_value - current_cell.h_value) / start.h_value

    if percentage > 1:
        percentage = 1
    elif percentage < 0:
        percentage = 0

    r = c2[0] - c1[0]
    g = c2[1] - c1[1]
    b = c2[2] - c1[2]

    return (int(percentage * r) + c1[0], int(percentage * g) + c1[1], int(percentage * b) + c1[2])
