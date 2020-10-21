import sudoku
import random


STUCK_LIMIT = 3
# CYCLE_LIMIT = 9999


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

    def allCellsValid(self):
        for cell in self.dom.values():
            if cell.isInvalid():
                return False
        return True

    def getMrvSortedVars(self):
        smolbois = []
        minlen = 9
        therest = []
        for i in range(9):
            for j in range(9):
                l = len(self.getDomain(i, j))
                if l > 1:
                    if l < minlen:
                        minlen = l
                        therest += smolbois
                        smolbois = [(i,j)]
                    elif l == minlen:
                        smolbois.append((i,j))
                    else:
                        therest.append((i,j))

        random.shuffle(therest)
        return smolbois + therest

def constrainRow(board, cells, r):
    solved = []
    allDoms = [cells.getDomain(r, i) for i in range(9)]
    row = board.getRow(r)

    for i in range(9):
        cell = cells.get(r, i)
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

    return cells, solved

def constrainCol(board, cells, c):
    solved = []
    allDoms = [cells.getDomain(i, c) for i in range(9)]
    col = board.getCol(c)

    for i in range(9):
        cell = cells.get(i, c)
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

    return cells, solved

def constrainSquare(board, cells, sqR, sqC):
    solved = []
    square = board.getSquareSq(sqR, sqC)
    allDoms = [cells.getDomain(j + sqR*3, i + sqC*3) for j in range(3) for i in range(3)]

    for i in range(sqR*3, sqR*3 + 3):
        for j in range(sqC*3, sqC*3 + 3):
            cell = cells.get(i, j)
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

    return cells, solved

def run(board, cells, trace):
    solved = []
    for i in range(9):
        cells, s = constrainRow(board, cells, i)
        solved += s
        cells, s = constrainCol(board, cells, i)
        solved += s
        cells, s = constrainSquare(board, cells, i%3, i//3)
        solved += s

    for r, c in solved:
        if trace:
            print(r, c, "->", cells.getVal(r, c))
        board.update(r, c, cells.getVal(r, c))

    return board, cells, len(solved)

def simpleSolve(board, cells, trace):
    cycle = 0
    stuck = 0
    while not board.isSolved() and stuck < STUCK_LIMIT and cycle < CYCLE_LIMIT:
        board, cells, numSolved = run(board, cells, trace)
        if numSolved > 0:
            stuck = 0
            if trace:
                print(board)
        else:
            stuck += 1
        cycle += 1

    if board.isSolved():
        if trace:
            print("Solved!")
        return board, cells, cycle
    else:
        return board, cells, -cycle

def getLcv(cells, mrv):
    check = [cells.getDomain(mrv[0], i) for i in range(9) if i != mrv[1]]
    check += [cells.getDomain(i, mrv[1]) for i in range(9) if i != mrv[0]]
    
    for i in range(3):
        i += (mrv[0]//3)*3
        if i == mrv[0]:
            continue
        for j in range(3):
            j += (mrv[1]//3)*3
            if j == mrv[0]:
                continue
            check.append(cells.getDomain(i, j))
    
    vals = cells.getDomain(mrv[0], mrv[1])
    count = [sum([val in dom for dom in check]) for val in vals]
    return count.index(min(count))

def backTrackingSolve(board):
    return backTrackingHelper(board, Cells(board), 0)        

def backTrackingHelper(board, cells, cycle):
    #if cycle > CYCLE_LIMIT:
    #    return -cycle

    #. print(board)

    # try a simple solution first
    try:
        stuck = 0
        while not board.isSolved() and stuck < STUCK_LIMIT:
            board, cells, numSolved = run(board, cells, False)
            if numSolved > 0:
                stuck = 0
            else:
                stuck += 1
            cycle += 1

        if board.isSolved():
            return cycle

        assert cells.allCellsValid()
    except:
        # failed. time to backtrack
        return -cycle

    # ok we're stuck. pick the cell w the smallest dom (min remaining values)
    # then pick the value which appears least among constrain doms (least constraining value)
    mrvs = cells.getMrvSortedVars()

    # i, j = 0, 0
    for mrv in mrvs:
        # i += 1
        # print("\n", i, end="")
        vals = cells.getDomain(mrv[0], mrv[1])
        assert len(vals) > 1
        random.shuffle(vals)
        lcv = getLcv(cells, mrv)

        # put lcv at the front of vals list
        vals.insert(0, vals.pop(lcv))

        for val in vals:
            # j += 1
            # print(j, end=' ')
            newBoard = board.copy()
            newCells = cells.copy()
            if (newBoard.update(mrv[0], mrv[1], val) == 0):
                # the new val is allowed. recurse.
                newCells.set(mrv[0], mrv[1], val)
                recurse = backTrackingHelper(newBoard, newCells, cycle)
                cycle += abs(recurse)
                if recurse > 0:
                    # success!
                    return cycle

    # everything failed :(
    #print("sad")
    return -cycle