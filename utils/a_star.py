from datetime import datetime
from . import helper_defs
from . import the_david_brian_heap
from copy import copy, deepcopy
from . import colors
import pygame


def weighted_a_star(start_node, goal_node, grid, heuristic, weight):
    helper_defs.reset_cells_in_grid(grid)
    helper_defs.set_cell_values(grid, goal_node, heuristic)
    helper_defs.set_cell_neighbors(grid)

    runtime_start = datetime.now()
    memory_start = helper_defs.memory()
    start_node.g_value = 0
    start_node.parent = None
    fringe = the_david_brian_heap.DavidsAndBriansHeapForCellPriorityWithAReallyLongName()
    fringe.insert(start_node, start_node.g_value + start_node.h_value * weight)
    start_node.in_fringe = True
    path_solution = []

    while not fringe.is_empty():

        current_cell = fringe.pop()

        if current_cell is goal_node:  # goal found
            runtime = datetime.now() - runtime_start
            memory_used = helper_defs.memory() - memory_start

            previous = goal_node.parent
            while previous.parent:
                path_solution.append(previous)
                previous = previous.parent

            print('RUNTIME: {} milliseconds'.format(runtime.microseconds / 1000))
            print('LENGTH OF PATH: {}'.format(sum([cell.g_value for cell in path_solution])))
            print('NODES EXPANDED: {}'.format(sum([cell.expanded_already for row in grid for cell in row])))
            print('MEMORY USED: {} bytes ({} MB)'.format(memory_used, memory_used / 1000000))

            return path_solution[::-1]

        current_cell.expanded_already = True
        for neighbor in current_cell.neighbors:

            if not neighbor.expanded_already:
                if not neighbor.in_fringe:
                    neighbor.g_value = 99999999
                    neighbor.parent = None
                if current_cell.g_value + helper_defs.calc_g_value(current_cell, neighbor) < neighbor.g_value:
                    neighbor.g_value = current_cell.g_value + helper_defs.calc_g_value(current_cell, neighbor)
                    neighbor.parent = current_cell
                    if neighbor.in_fringe:
                        fringe.remove(neighbor)
                        neighbor.in_fringe = False
                    fringe.insert(neighbor, neighbor.g_value + neighbor.h_value * weight)
                    neighbor.in_fringe = True

    print('No Path to Goal Found.')
    return


def uniform_cost_search(start_node, goal_node, grid):
    return weighted_a_star(start_node, goal_node, grid, None, 0)


def a_star(start_node, goal_node, grid, heuristic):
    helper_defs.reset_cells_in_grid(grid)
    helper_defs.set_cell_values(grid, goal_node, heuristic)
    helper_defs.set_cell_neighbors(grid)

    runtime_start = datetime.now()
    memory_start = helper_defs.memory()
    start_node.g_value = 0
    start_node.parent = None
    fringe = the_david_brian_heap.DavidsAndBriansHeapForCellPriorityWithAReallyLongName()
    fringe.insert(start_node, start_node.g_value + start_node.h_value)
    start_node.in_fringe = True
    path_solution = []

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

        if current_cell is goal_node:  # goal found
            runtime = datetime.now() - runtime_start
            memory_used = helper_defs.memory() - memory_start

            previous = goal_node.parent
            while previous.parent:
                path_solution.append(previous)
                previous = previous.parent

            print('RUNTIME: {} milliseconds'.format(runtime.microseconds / 1000))
            print('LENGTH OF PATH: {}'.format(sum([cell.g_value for cell in path_solution])))
            print('NODES EXPANDED: {}'.format(sum([cell.expanded_already for row in grid for cell in row])))
            print('MEMORY USED: {} bytes ({} MB)'.format(memory_used, memory_used / 1000000))

            return path_solution[::-1]

        current_cell.expanded_already = True
        for neighbor in current_cell.neighbors:

            if not neighbor.expanded_already:
                if not neighbor.in_fringe:
                    neighbor.g_value = 99999999
                    neighbor.parent = None
                if current_cell.g_value + helper_defs.calc_g_value(current_cell, neighbor) < neighbor.g_value:
                    neighbor.g_value = current_cell.g_value + helper_defs.calc_g_value(current_cell, neighbor)
                    neighbor.parent = current_cell
                    if neighbor.in_fringe:
                        fringe.remove(neighbor)
                        neighbor.in_fringe = False
                    fringe.insert(neighbor, neighbor.g_value + neighbor.h_value)
                    neighbor.in_fringe = True

    print('No Path to Goal Found.')

    return


def sequential_a_star(start_node, goal_node, grid, all_heuristics, weight1, weight2):
    helper_defs.reset_cells_in_grid(grid)
    helper_defs.set_cell_neighbors(grid)

    runtime_start = datetime.now()
    memory_start = helper_defs.memory()

    list_of_fringes = []
    list_of_grids = []

    for i in range(0, 5):
        list_of_fringes.append(the_david_brian_heap.DavidsAndBriansHeapForCellPriorityWithAReallyLongName())
        # list_of_grids.append({'start': copy(start_node), 'goal': copy(goal_node), 'grid': copy(grid)})

        list_of_grids.append({'grid': copy(grid)})
        list_of_grids[i]['start'] = list_of_grids[i]['grid'][start_node.row][start_node.col]
        list_of_grids[i]['goal'] = list_of_grids[i]['grid'][goal_node.row][goal_node.col]

        helper_defs.set_cell_values(list_of_grids[i]['grid'], goal_node, all_heuristics[i])

    for i in range(0, 5):
        current_start = list_of_grids[i]['start']
        current_goal = list_of_grids[i]['goal']
        current_start.g_value = 0.0
        current_goal.g_value = 999999999.0
        list_of_fringes[i].insert(current_start, key(current_start, current_goal, weight1, all_heuristics[i]))
        current_start.in_fringe = True


    while not list_of_fringes[0].is_empty():
        for i in range(1, 5):
            current_goal = list_of_grids[i]['goal']

            if not list_of_fringes[i].is_empty() and list_of_fringes[i].peek_min_priority() <= (weight2 * list_of_fringes[0].peek_min_priority()):
                if current_goal.g_value <= list_of_fringes[i].peek_min_priority():
                    if current_goal.g_value < 999999999.0: # goal found
                        runtime = datetime.now() - runtime_start
                        memory_used = helper_defs.memory() - memory_start

                        path_solution = []
                        previous = current_goal.parent
                        while previous.parent:
                            path_solution.append(previous)
                            previous = previous.parent

                        print('RUNTIME: {} milliseconds'.format(runtime.microseconds / 1000))
                        print('LENGTH OF PATH: {}'.format(sum([cell.g_value for cell in path_solution])))
                        print('NODES EXPANDED: {}'.format(sum([cell.expanded_already for row in list_of_grids[i]['grid'] for cell in row])))
                        print('MEMORY USED: {} bytes ({} MB)'.format(memory_used, memory_used / 1000000))

                        return path_solution[::-1]
                else:
                    cell_from_heap = list_of_fringes[i].pop()

                    for neighbor in cell_from_heap.neighbors:
                        if not neighbor.expanded_already:
                            if not neighbor.in_fringe:
                                neighbor.g_value = 999999999.0
                                neighbor.parent = None
                        if neighbor.g_value > cell_from_heap.g_value + helper_defs.calc_g_value(cell_from_heap, neighbor):
                            neighbor.g_value = cell_from_heap.g_value + helper_defs.calc_g_value(cell_from_heap, neighbor)
                            neighbor.parent = cell_from_heap
                            if neighbor.in_fringe:
                                list_of_fringes[i].remove(neighbor)
                                neighbor.in_fringe = False
                            list_of_fringes[i].insert(neighbor, key(neighbor, list_of_grids[i]['goal'], weight1, all_heuristics[i]))
                            neighbor.in_fringe = True

                    cell_from_heap.expanded_already = True

            else:
                if list_of_grids[0]['goal'].g_value <= list_of_fringes[0].peek_min_priority():
                    if list_of_grids[0]['goal'].g_value < 999999999.0: # goal found
                        runtime = datetime.now() - runtime_start
                        memory_used = helper_defs.memory() - memory_start

                        path_solution = []
                        previous = list_of_grids[0]['goal'].parent
                        while previous.parent:
                            path_solution.append(previous)
                            previous = previous.parent

                        print('RUNTIME: {} milliseconds'.format(runtime.microseconds / 1000))
                        print('LENGTH OF PATH: {}'.format(sum([cell.g_value for cell in path_solution])))
                        print('NODES EXPANDED: {}'.format(sum([cell.expanded_already for row in list_of_grids[i]['grid'] for cell in row])))
                        print('MEMORY USED: {} bytes ({} MB)'.format(memory_used, memory_used / 1000000))
                        return path_solution[::-1]
                else:
                    cell_from_heap = list_of_fringes[0].pop()

                    for neighbor in cell_from_heap.neighbors:
                        if not neighbor.expanded_already:
                            if not neighbor.in_fringe:
                                neighbor.g_value = 999999999.0
                                neighbor.parent = None
                        if neighbor.g_value > cell_from_heap.g_value + helper_defs.calc_g_value(cell_from_heap, neighbor):
                            neighbor.g_value = cell_from_heap.g_value + helper_defs.calc_g_value(cell_from_heap, neighbor)
                            neighbor.parent = cell_from_heap
                            if neighbor.in_fringe:
                                list_of_fringes[0].remove(neighbor)
                                neighbor.in_fringe = False
                            list_of_fringes[0].insert(neighbor, key(neighbor, list_of_grids[0]['goal'], weight1, all_heuristics[0]))
                            neighbor.in_fringe = True

                    cell_from_heap.expanded_already = True


    print('No Path to Goal Found.')

    return


def integrated_a_star(start_node, goal_node, grid, all_heuristics, weight1, weight2):
    helper_defs.reset_cells_in_grid(grid)
    helper_defs.set_cell_neighbors(grid)

    runtime_start = datetime.now()
    memory_start = helper_defs.memory()

    list_of_fringes = []
    start_node.g_value = 0
    goal_node.g_value = 999999999.0
    v_vals = {}

    for i in range(0, 5):
        list_of_fringes.append(the_david_brian_heap.DavidsAndBriansHeapForCellPriorityWithAReallyLongName())
        list_of_fringes[i].insert(start_node, key(start_node, goal_node, weight1, all_heuristics[i]))
        start_node.in_fringe = True

    while not list_of_fringes[0].is_empty():
        for i in range(1, 5):

            if not list_of_fringes[i].is_empty() and list_of_fringes[i].peek_min_priority() <= (weight2 * list_of_fringes[0].peek_min_priority()):
                if goal_node.g_value <= list_of_fringes[i].peek_min_priority():
                    if goal_node.g_value < 999999999.0:
                        runtime = datetime.now() - runtime_start
                        memory_used = helper_defs.memory() - memory_start

                        path_solution = []
                        previous = goal_node.parent
                        while previous.parent:
                            path_solution.append(previous)
                            previous = previous.parent

                        print('RUNTIME: {} milliseconds'.format(runtime.microseconds / 1000))
                        print('LENGTH OF PATH: {}'.format(sum([cell.g_value for cell in path_solution])))
                        print('NODES EXPANDED: {}'.format(sum([cell.expanded_already for row in grid for cell in row])))
                        print('MEMORY USED: {} bytes ({} MB)'.format(memory_used, memory_used / 1000000))

                        return path_solution[::-1]
                else:
                    cell_from_heap = list_of_fringes[i].pop()
                    for p in range(0,5):
                        list_of_fringes[p].remove(cell_from_heap)
                    v_vals[cell_from_heap] = cell_from_heap.g_value

                    for neighbor in cell_from_heap.neighbors:
                        if not neighbor.expanded_already:
                            if not neighbor.in_fringe:
                                neighbor.g_value = 999999999.0
                                neighbor.parent = None
                        if neighbor.g_value > cell_from_heap.g_value + helper_defs.calc_g_value(cell_from_heap, neighbor):
                            neighbor.g_value = cell_from_heap.g_value + helper_defs.calc_g_value(cell_from_heap, neighbor)
                            neighbor.parent = cell_from_heap
                            if neighbor.in_fringe:
                                list_of_fringes[0].remove(neighbor)
                                neighbor.in_fringe = False
                            list_of_fringes[0].insert(neighbor, key(neighbor, goal_node, weight1, all_heuristics[0]))
                            neighbor.in_fringe = True
                            for z in range(1,5):
                                if key(neighbor, goal_node, weight1, all_heuristics[i]) <= weight2*key(neighbor, goal_node, weight1, all_heuristics[0]):
                                    list_of_fringes[z].insert(neighbor, key(neighbor, goal_node, weight1, all_heuristics[0]))
                                    neighbor.in_fringe = True

                    cell_from_heap.expanded_already = True

            else:
                if goal_node.g_value <= list_of_fringes[0].peek_min_priority():
                    if goal_node.g_value < 999999999.0:
                        runtime = datetime.now() - runtime_start
                        memory_used = helper_defs.memory() - memory_start

                        path_solution = []
                        previous = goal_node.parent
                        while previous.parent:
                            path_solution.append(previous)
                            previous = previous.parent

                        print('RUNTIME: {} milliseconds'.format(runtime.microseconds / 1000))
                        print('LENGTH OF PATH: {}'.format(sum([cell.g_value for cell in path_solution])))
                        print('NODES EXPANDED: {}'.format(sum([cell.expanded_already for row in grid for cell in row])))
                        print('MEMORY USED: {} bytes ({} MB)'.format(memory_used, memory_used / 1000000))

                        return path_solution[::-1]
                else:
                    cell_from_heap = list_of_fringes[0].pop()
                    for p in range(0,5):
                        list_of_fringes[p].remove(cell_from_heap)
                    v_vals[cell_from_heap] = cell_from_heap.g_value

                    for neighbor in cell_from_heap.neighbors:
                        if not neighbor.expanded_already:
                            if not neighbor.in_fringe:
                                neighbor.g_value = 999999999.0
                                neighbor.parent = None
                        if neighbor.g_value > cell_from_heap.g_value + helper_defs.calc_g_value(cell_from_heap, neighbor):
                            neighbor.g_value = cell_from_heap.g_value + helper_defs.calc_g_value(cell_from_heap, neighbor)
                            neighbor.parent = cell_from_heap
                            if neighbor.in_fringe:
                                list_of_fringes[0].remove(neighbor)
                                neighbor.in_fringe = False
                            list_of_fringes[0].insert(neighbor, key(neighbor, goal_node, weight1, all_heuristics[0]))
                            neighbor.in_fringe = True
                            for z in range(1,5):
                                if key(neighbor, goal_node, weight1, all_heuristics[i]) <= weight2*key(neighbor, goal_node, weight1, all_heuristics[0]):
                                    list_of_fringes[z].insert(neighbor, key(neighbor, goal_node, weight1, all_heuristics[0]))
                                    neighbor.in_fringe = True

                    cell_from_heap.expanded_already = True

    print('No Path to Goal Found.')

    return


def key(node, current_goal, weight1, current_heuristic):
    return node.g_value + weight1 * current_heuristic(node, current_goal)

