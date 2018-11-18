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

# def populate_puzzle(puzzle):
#     for i in range(len(puzzle.config)):
#         for j in range(len(puzzle.config[i])):
#             if puzzle.cell_is_editable[i][j]:
#                 puzzle.config[i][j] = random.randint(1,9)

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

# my brain can't think anymore
# def get_next_best(puzzle):
#     next = []
#     dummy_puzzle = copy.deepcopy(puzzle)
#     for i in range(len(dummy_puzzle.config)):
#         row_candidates = [x for x in range(1,len(dummy_puzzle.config[0]) + 1)]
#         row_candidates_indices = [x for x in range(lendummy_puzzle.config[0]))]
#         for j in range(len(puzzle.config[i])):
#             if not puzzle.cell_is_editable[i][j]:
#                 row_candidates.remove(puzzle.config[i][j])
#                 row_candidates_indices.remove(j)
#         row_permutations = itertools.permutations(row_candidates)
#         for row_perm in row_permutations:
#             for r_i in row_candidates_indices:
#                 dummy_puzzle.config[i][r_i] =


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



def do_search(puzzle):
    curr_puzzle = puzzle
    populate_puzzle(curr_puzzle)
    cell_being_changed = [0,0]
    row_being_shuffled = 0

    temp = 1000
    prob = 0
    cooling_schedule = 10
    itt = 0
    iterations = 0

    while(curr_puzzle.get_total_conflicts() != 0):
        iterations += 1
        if iterations == 50:
            return do_search(puzzle) #really

        print(iterations)
        # not gonna use mod, incase it overflows
        # this should work the same way
        if row_being_shuffled >= 9:
            row_being_shuffled = 0

        # if cell_being_change[0] > 8:
        #     cell_being_change[0] = 0
        #
        # if cell_being_change[1] > 8:
        #     cell_being_change[0] = 0

        for i in range(len(curr_puzzle.config)):
            for j in range(len(curr_puzzle.config[i])):
                new_puzzle = SudokuPuzzle(copy.deepcopy(curr_puzzle.config))
                new_puzzle.cell_is_editable = copy.deepcopy(curr_puzzle.cell_is_editable)
                for k in range(1,10):
                    if new_puzzle.cell_is_editable[i][j]:
                        new_puzzle.config[i][j] = k
                    # prob = math.e**((curr_puzzle.get_total_conflicts() - new_puzzle.get_total_conflicts()) / temp)
                    # # print(prob)
                    # # input()
                    # if prob > random.random():
                    #     curr_puzzle = new_puzzle
                    #     print(curr_puzzle.get_total_conflicts())
                    #     print(prob)
                    #     break
                    if new_puzzle.get_total_conflicts() < curr_puzzle.get_total_conflicts():
                        curr_puzzle = new_puzzle
                        print("Total conflicts : " +str(curr_puzzle.get_total_conflicts()))
                        iterations = 0
                        break
                    elif random.random() > .9 and new_puzzle.get_total_conflicts() == curr_puzzle.get_total_conflicts():
                        curr_puzzle = new_puzzle
                        break

        # next_puzzles = permute_row(curr_puzzle,row_being_shuffled)
        #
        # for next_puzzle in next_puzzles:
            # if next_puzzle.get_total_conflicts() < curr_puzzle.get_total_conflicts():
        #         curr_puzzle = next_puzzle
        #         print(curr_puzzle.get_total_conflicts())

        # row_being_shuffled += 1
        # if itt % cooling_schedule == 0:
        #     if temp > .01:
        #         temp -= .01


    return curr_puzzle


def main():
    samples = open("C:\\Users\\dell\\Desktop\\sudoku_puzzles.txt","r")
    puzzles = []

    for p in samples:
        puzzles.append(create_puzzle(p))

    p = puzzles[0]
    print(do_search(p))
    # do_search(p)
    # for i in range(9):
    #   print('\t'.join(p[i*9:i*9+9]))



if __name__ == '__main__':
    main()
