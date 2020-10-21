import sudoku
import random
from utils import *

TESTBOARD = 6
STUCK_LIMIT = 3
CYCLE_LIMIT = 100
STATS_MODE = True
SOLVER = "backTrackingSolve"
# "simpleSolve"

class Cell:
    def __init__(self, val, copied=False):
        if not copied:
            assert val>=0 and val<10

            if val != 0:
                self.domain = [val]
            else:
                self.domain = list(range(1, 10))
        else:
            self.domain = val

    def copy(self):
        return Cell(self.domain.copy(), True)

    def constrain(self, cons):
        if not self.isSet():
            self.domain = [i for i in self.domain if i not in cons]
            assert len(self.domain) >= 1
            if self.isSet():
                return 1
        return 0

    def set(self, val):
        assert val>0 and val<10
        self.domain = [val]

    def getDomain(self):
        return self.domain

    def isSet(self):
        return len(self.domain) == 1

    def isInvalid(self):
        return len(self.domain) < 1

    # def getVal(self):
    #     if self.isSet(r, c):
    #         return self.domain[0]
    #     else:
    #         return None

class Cells:
    def __init__(self, board, copied=False):
        if not copied:
            self.dom = {}

            for i in range(9):
                for j in range(9):
                    self.dom[(i,j)] = Cell(board.getElement(i, j))  
        else:
            self.dom = board  

    # def constrain(self, cons, r, c):
    #     if len(self.dom[(r,c)]) > 1:
    #         self.dom[(r,c)] = [i for i in self.dom[(r,c)] if i not in cons]
    #         if len(self.dom[(r,c)]) == 1:
    #             return 1
    #     return 0

    def set(self, r, c, val):
        assert val>0 and val<10
        self.dom[(r,c)] = Cell(val)

    def copy(self):
        newDom = {}
        for key in self.dom:
            newDom[key] = self.dom[key].copy()
        return Cells(newDom, True)

    def get(self, r, c):
        return self.dom[(r,c)]

    def getDomain(self, r, c):
        # print(r, c, end="|")
        return self.dom[(r,c)].getDomain()

    def isSet(self, r, c):
        return self.dom[(r,c)].isSet()

    def getVal(self, r, c):
        if self.isSet(r, c):
            return self.dom[(r,c)].getDomain()[0]
        else:
            return None

    def mrv(self):
        smolbois = []
        minlen = 9
        for i in range(9):
            for j in range(9):
                l = len(self.getDomain(i, j))
                if l > 1:
                    if l < minlen:
                        minlen = l
                        smolbois = [(i,j)]
                    elif l == minlen:
                        smolbois.append((i,j))
        # print(minlen)
        return smolbois

    def getAllExcept(self, exclude):
        result = []
        for key in self.dom:
            if key in exclude or self.dom[key].isInvalid():
                continue
            else:
                result.append(key)
        return result

class Solver:
    def __init__(self, board):
        self.board = board
        # self.cells = [[Cell(self.board.getElement(r, c)) for c in range(9)] for r in range(9)]
        self.cells = Cells(self.board)

    def constrainRow(self, r):
        solved = []
        allDoms = [self.cells.getDomain(r, i) for i in range(9)]
        row = self.board.getRow(r)

        for i in range(9):
            cell = self.cells.get(r, i)
            if cell.isSet():
                continue

            # rm all row vals from row domains
            if cell.constrain(row) == 1:
                solved.append((r, i))
                continue


            # check if any dom has unique values
            check = allDoms[:i] + allDoms[i+1:]
            for val in cell.getDomain():
                if sum([val in dom for dom in check]) == 0:
                    cell.set(val)
                    solved.append((r, i))

        return solved

    def constrainCol(self, c):
        solved = []
        allDoms = [self.cells.getDomain(i, c) for i in range(9)]
        col = self.board.getCol(c)

        for i in range(9):
            cell = self.cells.get(i, c)
            if cell.isSet():
                continue

            # rm all col vals from col domains
            if cell.constrain(col) == 1:
                solved.append((i, c))
                continue

            # check if any dom has unique values
            check = allDoms[:i] + allDoms[i+1:]
            for val in cell.getDomain():
                if sum([val in dom for dom in check]) == 0:
                    cell.set(val)
                    solved.append((i, c))

        return solved

    def constrainSquare(self, sqR, sqC):
        solved = []
        square = self.board.getSquareSq(sqR, sqC)
        allDoms = [self.cells.getDomain(j + sqR*3, i + sqC*3) for j in range(3) for i in range(3)]

        for i in range(sqR*3, sqR*3 + 3):
            for j in range(sqC*3, sqC*3 + 3):
                cell = self.cells.get(i, j)
                if cell.isSet():
                    continue

                # rm all sq vals from sq domains
                if cell.constrain(square) == 1:
                    solved.append((i, j))
                    continue

                # check if any dom has unique values
                check = allDoms[:i] + allDoms[i+1:]
                for val in cell.getDomain():
                    if sum([val in dom for dom in check]) == 0:
                        cell.set(val)
                        solved.append((i, j))

        return solved

    def run(self, trace):
        solved = []
        for i in range(9):
            solved += self.constrainRow(i)
            solved += self.constrainCol(i)
            solved += self.constrainSquare(i%3, i//3)

        for r, c in solved:
            if trace:
                print(r, c, "->", self.cells.getVal(r, c))
            self.board.update(r, c, self.cells.getVal(r, c))

        return len(solved)

    def simpleSolve(self, trace):
        cycle = 0
        stuck = 0
        while not self.board.isSolved() and stuck < STUCK_LIMIT and cycle < CYCLE_LIMIT:
            if self.run(trace) > 0:
                stuck = 0
                if trace:
                    print(self.board)
            else:
                stuck += 1
            cycle += 1

        if self.board.isSolved():
            if trace:
                print("Solved!")
            return cycle
        else:
            return -cycle

    def getLcv(self, mrv):
        check = [self.cells.getDomain(mrv[0], i) for i in range(9) if i != mrv[1]]
        check += [self.cells.getDomain(i, mrv[1]) for i in range(9) if i != mrv[0]]
        
        for i in range(3):
            i += (mrv[0]//3)*3
            if i == mrv[0]:
                continue
            for j in range(3):
                j += (mrv[1]//3)*3
                if j == mrv[0]:
                    continue
                check.append(self.cells.getDomain(i, j))
        
        vals = self.cells.getDomain(mrv[0], mrv[1])
        count = [sum([val in dom for dom in check]) for val in vals]
        return count.index(min(count))        

    def backTrackingSolve(self, cycle = 0):
        backtrack = Stack()
        while not self.board.isSolved() and cycle < CYCLE_LIMIT:
            # try a simple solution first
            try:
                simp = self.simpleSolve(False)
                cycle += abs(simp)
                if simp > 0:
                    return cycle
            except:
                print(cycle, end=",")

            # ok we're stuck. pick the cell w the smallest dom (min remaining values)
            # then pick the value which appears least among constrain doms (least constraining value)
            mrvs = self.cells.mrv()
            random.shuffle(mrvs)
            mrvs += self.cells.getAllExcept(mrvs)
            for mrv in mrvs:
                vals = self.cells.getDomain(mrv[0], mrv[1])
                lcv = self.getLcv(mrv)
                vals.insert(0, vals.pop(lcv))
                for val in vals:
                    # print("old")
                    # self.printBoard()
                    backtrack.push((self.cells.copy(), self.board.copy()))
                    if (self.board.update(mrv[0], mrv[1], val) == 0):
                        self.cells.set(mrv[0], mrv[1], val)
                        result = 1
                        while result != 0:
                            try:
                                result = self.run(False)
                                cycle += 1
                            except:
                                result = 0
                        if self.board.isSolved():
                            return cycle
                    self.cells, self.board = backtrack.pop()
                    # print("renew")
                    # self.printBoard()
            cycle += 1

        return -cycle

    def printBoard(self):
        print(self.board)


if STATS_MODE:
    cycles = []
    failed = []
    bigboi = 0
    smolboi = 0
    for i in range(51):
        print(i)
        solve = Solver(sudoku.Board(generateBoard(i)))
        if SOLVER == "backTrackingSolve":
            cycle = solve.backTrackingSolve()
        else:
            cycle = solve.simpleSolve(False)
        if cycle > 0:
            cycles.append(cycle)
            if cycle == max(cycles):
                bigboi = i
            if cycle == min(cycles):
                smolboi = i
        else:
            failed.append((i, cycle))
        solve.printBoard()

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
else:
    solve = Solver(sudoku.Board(generateBoard(TESTBOARD)))
    solve.backTrackingSolve()
