import random
import sudoku
from solver import *

TESTBOARD = 6
STATS_MODE = 10
SOLVER = "backTrackingSolve"
# "simpleSolve"

def generateBoard(num=-1):
    if num < 0 or num > 50:
        num = random.randint(0, 50)
    f = open("sudoku_boards.txt", "r")
    data = f.read().split("\n")
    f.close()
    num = 10 * num + 1
    return [[int(char) for char in data[num + i]] for i in range(9)]

if STATS_MODE == 0:
    cycles = []
    failed = []
    bigboi = 0
    smolboi = 0
    for i in range(51):
        print(i)
        board = sudoku.Board(generateBoard(i))
        if SOLVER == "backTrackingSolve":
            cycle = backTrackingSolve(board)
        else:
            cycle = simpleSolve(board, Cells(board), False)[2]
        if cycle > 0:
            cycles.append(cycle)
            if cycle == max(cycles):
                bigboi = i
            if cycle == min(cycles):
                smolboi = i
        else:
            failed.append((i, cycle))
        print(board)

    print()
    print(SOLVER)
    print("-"*32)
    success = len(cycles)
    print("Solved:", success, "/ 51")
    print("Success Rate:", success/51*100)
    print("Ave Cycles:", sum(cycles)/success)
    print("Max Cycles:", max(cycles))
    print("^ Board", bigboi)
    print("Min Cycles:", min(cycles))
    print("^ Board", smolboi)
elif STATS_MODE > 0:
    sumCycles = 0
    success = 0
    for i in range(51):
        count = 0
        for j in range(STATS_MODE):
            board = sudoku.Board(generateBoard(i))
            cycle = backTrackingSolve(board)
            if cycle > 0:
                sumCycles += cycle
                count += 1
        success += count
        if count < STATS_MODE:
            print(i, ':', count)
    print("Solved:", success, "/", str(51*STATS_MODE))
    print("Success Rate:", success/51/STATS_MODE*100)
    print("Ave Cycles:", sumCycles/success)
else:
    print("hey")
    # print(backTrackingSolve(sudoku.Board(generateBoard(TESTBOARD))))