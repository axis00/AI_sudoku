import random
import copy
import itertools
import sys
import math

class SudokuPuzzle:
    def __init__(self, init_config):
        self.config = init_config
        self.cell_is_editable = [[False for i in range(len(init_config))] for j in range(len(init_config[0]))]
        self.conflicts = SudokuPuzzle.__count_conflicts(self.config)
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

# returns an array of puzzles where the row indicated has been permutated??
def permute_row(puzzle,row):
    res = []
    candidates = [x for x in range(1,len(puzzle.config[row]) + 1)]
    candidate_indices = [x for x in range(len(puzzle.config[row]))]
    for i in range(len(puzzle.config[row])):
        if not puzzle.cell_is_editable[row][i]:
            candidates.remove(puzzle.config[row][i])
            candidate_indices.remove(i)

    permutations = list(itertools.permutations(candidates))
    for r in permutations:
        r = list(r)
        new_puzzle = SudokuPuzzle(copy.deepcopy(curr_puzzle.config))
        new_puzzle.cell_is_editable = copy.deepcopy(curr_puzzle.cell_is_editable)
        for i in candidate_indices:
            new_puzzle.config[row][i] = r.pop()
        res.append(new_puzzle)
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
    curr_puzzle = puzzle
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
        sys.stdout.write("\rConflicts: %3d" % curr_puzzle.get_total_conflicts())
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
                    elif random.random() > .9995 and failed_iterations > 10:
                        curr_puzzle = new_puzzle
                        res["wrong_steps"] += 1
                        break
            failed_iterations += 1
            res["failed_attemps"] = failed_iterations
            sys.stdout.write("\rConflicts: %4d" % curr_puzzle.get_total_conflicts())
            sys.stdout.flush()

    res["solution"] = curr_puzzle
    return res


def main():
    samples = open("sudoku_puzzles.txt","r")
    puzzles = []

    for p in samples:
        puzzles.append(create_puzzle(p))

    p = puzzles[0]
    print("\n" + str(do_stochastic_search(p)['solution']))
    print("\n" + str(do_search(p)['solution']))

if __name__ == '__main__':
    main()
