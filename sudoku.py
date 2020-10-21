class Board:
    def __init__(self, newBoard=None):
        if newBoard == None:
            self.board = [[1, 0, 0, 4, 8, 9, 0, 0, 6], [7, 3, 0, 0, 0, 0, 0, 4, 0], [0, 0, 0, 0, 0, 1, 2, 9, 5], [0, 0, 7, 1, 2, 0, 6, 0, 0], [5, 0, 0, 7, 0, 3, 0, 0, 8], [0, 0, 6, 0, 9, 5, 7, 0, 0], [9, 1, 4, 6, 0, 0, 0, 0, 0], [0, 2, 0, 0, 0, 0, 0, 3, 7], [8, 0, 0, 5, 1, 2, 0, 0, 4]]
        else:
            self.board = newBoard

    def __str__(self):
        result = ""
        for i in range(9):
            if i%3 == 0:
                result += "=" * 31 + "\n"
            for j in range(9):
                if j%3 == 0:
                    result += "| "
                else:
                    result += " "
                if self.board[i][j] == 0:
                    result += "  "
                else:
                    result += str(self.board[i][j]) + " "
            result += "|\n"
        result += "=" * 31 + "\n"
        return result

    def copy(self):
        newBoard = []
        for row in self.board:
            newRow = []
            for col in row:
                newRow.append(col)
            newBoard.append(newRow)
        return Board(newBoard)

    def getBoard(self):
        return self.board

    def getElement(self, r, c):
        return self.board[r][c]

    def getCol(self, c):
        return [row[c] for row in self.board]

    def getRow(self, r):
        return self.board[r]

    def getSquare(self, r, c):
        return self.getSquareSq(r//3, c//3)

    def getSquareSq(self, sqR, sqC):
        return [self.board[j + sqR*3][i + sqC*3] for j in range(3) for i in range(3)]

    def update(self, r, c, val):
        if self.board[r][c] != 0:
            # print("Error:", r, ",", c, "is already set.")
            return -1
        elif val == 0:
            # print("Error: Cannot set to 0.")
            return -2
        elif val in self.board[r]:
            # print("Error: Row", r, "already has a ", val, ".")
            return -3
        elif val in self.getCol(c):
            # print("Error: Col", c, "already has a ", val, ".")
            return -4
        elif val in self.getSquare(r, c):
            # print("Error:", r, ",", c, "'s square already has a", val, ".")
            return -5
        else:
            self.board[r][c] = val
            return 0

    def isSolved(self):
        return sum([0 in r for r in self.board]) == 0