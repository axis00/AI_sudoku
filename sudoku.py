import sys
import random
import plotly
import plotly.graph_objs as go

from plotly import tools
import copy
import itertools
import sys
import math

class SudokuPuzzle:
    def __init__(self, init_config):
        self.config = init_config
        self.cell_is_editable = [[False for i in range(len(init_config))] for j in range(len(init_config[0]))]
        self.conflicts = SudokuPuzzle.__count_conflicts(self.config)
        self.blanks = 0
        for i in range(len(self.config)):
            for j in range(len(self.config[0])):
                if int(init_config[i][j]) == 0:
                    self.cell_is_editable[i][j] = True
                else:
                    self.cell_is_editable[i][j] = False

    # returns a 2d array where each element represents the number of conflicts
    # each cell in the config has
    def __count_conflicts(config):
        res = [[0 for i in range(len(config))] for j in range(len(config[0]))]
        for i in range(len(res)):
            for j in range(len(res[i])):
                res[i][j] = SudokuPuzzle.__count_cell_conflicts(i,j,config)
        return res

    # returns the total number of conflicts in the whole current config
    def get_total_conflicts(self):
        self.conflicts = SudokuPuzzle.__count_conflicts(self.config)
        res = 0
        for i in range(len(self.conflicts)):
            for j in range(len(self.conflicts[i])):
                res += self.conflicts[i][j]
        return res

    # helper function to count the conflicts of a given cell
    def __count_cell_conflicts(row,col,config):
        value = config[row][col]
        conflicts = 0
        # column count
        for i in range(len(config)):
            if i != row and value == config[i][col]:
                conflicts += 1
        # 3x3 count
        # helper function to get the range of the indeces to check when counting
        # the conflicts in the 3x3 grid that the cell belong to
        # couldn't think of a mathematical way to do it
        def local_range(x):
            if x in [0,1,2]:
                return 0,3
            if x in [3,4,5]:
                return 3,6
            if x in [6,7,8]:
                return 6,9

        row_range = local_range(row)
        col_range = local_range(col)
        for i in range(row_range[0],row_range[1]):
            for j in range(col_range[0],col_range[1]):
                if i != row and j != col and value == config[i][j]:
                    conflicts += 1

        # row counting
        for j in range(len(config)):
            if j != col and value == config[row][j]:
                conflicts += 1

        return conflicts

    def __str__(self):
        res = ""
        for row in self.config:
            res += str(row) + "\n"

        return res

def create_puzzle(puzzle_arr):
    n_row = 9
    n_col = 9
    config = [[ 0 for i in range(n_row) ] for j in range(n_col) ]

    for i in range(n_row):
        for j in range(n_col):
            config[i][j] = int(puzzle_arr[ i * n_col + j ])

    return SudokuPuzzle(config)

# function that fills in all the blank cells(numbered 0) per row_range
# each row is guaranteed not to have conflicts
def populate_puzzle(puzzle):
    # get numbers already in the row
    for i in range(len(puzzle.config)):
        row = puzzle.config[i]
        candidates = [x for x in range(1,len(row) + 1)]
        random.shuffle(candidates)
        # purge all the values already in the puzzle
        for val in row:
            if val != 0:
                candidates.remove(val)
        # place the remaining values in the empty cells
        for j in range(len(row)):
            val = puzzle.config[i][j]
            if val == 0:
                puzzle.config[i][j] = candidates.pop()

                puzzle.config[i][j] = random.randint(1,9)

# function that returns an new puzzle object that has has the row indicated shuffled
# shuffling happens to element with conflicts greater than 0
def shuffle_puzzle_row(puzzle,row):
    res = copy.deepcopy(puzzle)
    conflict_indices  = []
    conflict_values = []

    for i in range(len(res.config[row])):
        if res.conflicts[row][i] != 0 and res.cell_is_editable[row][i]:
            conflict_indices.append(i)
            conflict_values.append(res.config[row][i])

    random.shuffle(conflict_values)
    for i in conflict_indices:
        if res.cell_is_editable[row][i]:
            res.config[row][i] = conflict_values.pop()

    return res



def do_gradient_search(puzzle):
    curr_puzzle = puzzle
    populate_puzzle(curr_puzzle)

    failed_iterations = 0

    while(curr_puzzle.get_total_conflicts() != 0):
        failed_iterations += 1
        print(failed_iterations)
        if failed_iterations == 50:
            return do_gradient_search(puzzle)
        #
        # print(iterations)
        for i in range(len(curr_puzzle.config)):
            for j in range(len(curr_puzzle.config[i])):
                if curr_puzzle.get_total_conflicts == 0:
                    return curr_puzzle
                new_puzzle = SudokuPuzzle(copy.deepcopy(curr_puzzle.config))
                new_puzzle.cell_is_editable = copy.deepcopy(curr_puzzle.cell_is_editable)
                best_puzzle = curr_puzzle
                for k in range(1,10):
                    if new_puzzle.cell_is_editable[i][j]:
                        new_puzzle.config[i][j] = k
                    if new_puzzle.get_total_conflicts() < best_puzzle.get_total_conflicts():
                        best_puzzle = SudokuPuzzle(copy.deepcopy(new_puzzle.config))
                        best_puzzle.cell_is_editable = copy.deepcopy(new_puzzle.cell_is_editable)
                        print("Total conflicts : " + str(new_puzzle.get_total_conflicts()))
                        failed_iterations = 0
                    elif random.random() > .9 and new_puzzle.get_total_conflicts() == best_puzzle.get_total_conflicts():
                        best_puzzle = SudokuPuzzle(copy.deepcopy(new_puzzle.config))
                        best_puzzle.cell_is_editable = copy.deepcopy(new_puzzle.cell_is_editable)
                        print("Total conflicts : " + str(new_puzzle.get_total_conflicts()))
                curr_puzzle = best_puzzle
    return curr_puzzle

def do_search(puzzle,prev = None):
    res = {"restarts" : 0,
            "solution" : None,
            "nodes_visited" : 0,
            "steps" : 0,
            "failed_attemps" : 0}


    if prev:
        res = prev
    curr_puzzle = copy.deepcopy(puzzle)
    populate_puzzle(curr_puzzle)

    failed_iterations = 0

    while(curr_puzzle.get_total_conflicts() != 0):
        if failed_iterations == 20:
            print("\nRestarting")
            res["restarts"] += 1
            return do_search(puzzle,res)

        for i in range(len(curr_puzzle.config)):
            for j in range(len(curr_puzzle.config[i])):
                new_puzzle = SudokuPuzzle(copy.deepcopy(curr_puzzle.config))
                new_puzzle.cell_is_editable = copy.deepcopy(curr_puzzle.cell_is_editable)
                for k in range(1,10):
                    if new_puzzle.cell_is_editable[i][j]:
                        new_puzzle.config[i][j] = k
                        res["nodes_visited"] += 1
                    if new_puzzle.get_total_conflicts() < curr_puzzle.get_total_conflicts():
                        curr_puzzle = new_puzzle
                        res["steps"] += 1
                        failed_iterations = 0
                        break
                    elif random.random() > .9 and new_puzzle.get_total_conflicts() == curr_puzzle.get_total_conflicts():
                        curr_puzzle = new_puzzle
                        res["steps"] += 1
                        break
        failed_iterations += 1
        res["failed_attemps"] = failed_iterations
        sys.stdout.write("\rRandom Restart - Conflicts: %3d" % curr_puzzle.get_total_conflicts())
        sys.stdout.flush()

    res["solution"] = curr_puzzle
    return res

def do_stochastic_search(puzzle):
    res = {"wrong_steps" : 0,
            "solution" : None,
            "nodes_visited" : 0,
            "steps" : 0,
            "failed_attemps" : 0}
    curr_puzzle = puzzle
    populate_puzzle(curr_puzzle)

    failed_iterations = 0

    while(curr_puzzle.get_total_conflicts() != 0):
        for i in range(len(curr_puzzle.config)):
            for j in range(len(curr_puzzle.config[i])):
                new_puzzle = SudokuPuzzle(copy.deepcopy(curr_puzzle.config))
                new_puzzle.cell_is_editable = copy.deepcopy(curr_puzzle.cell_is_editable)
                for k in range(1,10):
                    if new_puzzle.cell_is_editable[i][j]:
                        new_puzzle.config[i][j] = k
                        res["nodes_visited"] += 1
                    if new_puzzle.get_total_conflicts() < curr_puzzle.get_total_conflicts():
                        curr_puzzle = new_puzzle
                        res["steps"] += 1
                        failed_iterations = 0
                        break
                    elif random.random() > .9 and new_puzzle.get_total_conflicts() == curr_puzzle.get_total_conflicts():
                        curr_puzzle = new_puzzle
                        res["steps"] += 1
                        break
                    elif random.random() > .999 and failed_iterations > 10:
                        curr_puzzle = new_puzzle
                        res["wrong_steps"] += 1
                        break
            failed_iterations += 1
            res["failed_attemps"] = failed_iterations
            sys.stdout.write("\rStochastic - Conflicts: %4d" % curr_puzzle.get_total_conflicts())
            sys.stdout.flush()

    res["solution"] = curr_puzzle
    return res

def plot(x_val, y_val, line_name):
    trace = go.Scatter(
        x = x_val,
        y = y_val,
        mode = 'lines',
        name = line_name
    )
    return trace

def get_plotdata():
    res = {}
    wrong_steps_points = []
    s_num_of_steps_points = []
    s_num_of_nodes_visited_points = []
    r_restarts_points = []
    r_num_of_steps_points = []
    r_num_of_nodes_visited_points = []
    # list of lists(l) of length 2 where l[0] is the solution detph and l[1] is the max_frontier_size

    samples = open("sudoku_puzzles.txt","r")
    puzzles = []

    for p in samples:
        puzzles.append(create_puzzle(p))

    for i in range(len(puzzles)):
        p = puzzles[i]
        print("\n Puzzle : %d" % i)
        itt = 10
        s_res = None
        r_res = None
        for j in range(itt):
            temp_s_res = do_stochastic_search(copy.deepcopy(p))
            if s_res:
                s_res["wrong_steps"] += temp_s_res["wrong_steps"]
                s_res["nodes_visited"] += temp_s_res["nodes_visited"]
                s_res["steps"] += temp_s_res["nodes_visited"]
                s_res["failed_attemps"] += temp_s_res["failed_attemps"]
            else:
                s_res = temp_s_res

            temp_r_res = do_search(copy.deepcopy(p))
            if r_res:
                r_res["restarts"] += temp_r_res["restarts"]
                r_res["nodes_visited"] += temp_r_res["nodes_visited"]
                r_res["steps"] += temp_r_res["nodes_visited"]
                r_res["failed_attemps"] += temp_r_res["failed_attemps"]
            else:
                r_res = temp_r_res

        # averaging
        s_res["wrong_steps"] = s_res["wrong_steps"] / itt
        s_res["nodes_visited"] = s_res["nodes_visited"] / itt
        s_res["steps"] = s_res["nodes_visited"] / itt
        s_res["failed_attemps"] = s_res["failed_attemps"] / itt

        r_res["restarts"] = r_res["restarts"] / itt
        r_res["nodes_visited"] = r_res["nodes_visited"] / itt
        r_res["steps"] = r_res["nodes_visited"] / itt
        r_res["failed_attemps"] = r_res["failed_attemps"] / itt

        wrong_steps_points.append([i,s_res['wrong_steps']])
        s_num_of_steps_points.append([i,s_res['steps']])
        s_num_of_nodes_visited_points.append([i,s_res['nodes_visited']])
        r_restarts_points.append([i,r_res['restarts']])
        r_num_of_steps_points.append([i,r_res['steps']])
        r_num_of_nodes_visited_points.append([i,r_res['nodes_visited']])


    res['wrong_steps'] = plot(
            [p[0] for p in wrong_steps_points],
            [p[1] for p in wrong_steps_points],
            "Stochastic - Num of wrong steps"
        )

    res['s_steps'] = plot(
            [p[0] for p in s_num_of_steps_points],
            [p[1] for p in s_num_of_steps_points],
            "Stochastic - Num of steps"
        )

    res['s_nodes_visited'] = plot(
            [p[0] for p in s_num_of_nodes_visited_points],
            [p[1] for p in s_num_of_nodes_visited_points],
            "Stochastic - Num of nodes visited points"
        )

    res['restarts'] = plot(
            [p[0] for p in r_restarts_points],
            [p[1] for p in r_restarts_points],
            "Random Restarts"
        )
    res['r_steps'] = plot(
            [p[0] for p in r_num_of_steps_points],
            [p[1] for p in r_num_of_steps_points],
            "Random Restart - Num of steps"
        )
    res['r_nodes_visited'] = plot(
            [p[0] for p in r_num_of_nodes_visited_points],
            [p[1] for p in r_num_of_nodes_visited_points],
            "Random Restart - Num of nodes visited points"
        )

    return res

def main():
    plots = get_plotdata()
    plotdata = [
            plots['wrong_steps'],
            plots['s_steps'],
            plots['s_nodes_visited'],
            plots['restarts'],
            plots['r_steps'],
            plots['r_nodes_visited']
        ]

    plotly.offline.plot({
    "data": plotdata,
    "layout": go.Layout(
            title="Sudoku Local Search Plot Data( Averaged over 10 iterations)",
            xaxis={'title':"Instance"},
            yaxis={'title':"Unit"}
        )
    }, auto_open=True, filename='sudoku-local-search-plot-data.html')

if __name__ == '__main__':
    main()
