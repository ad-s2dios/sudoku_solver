#import sudoku
import random

def generateBoard(num=-1):
    if num < 0 or num > 50:
        num = random.randint(0, 50)
    f = open("sudoku_boards.txt", "r")
    data = f.read().split("\n")
    f.close()
    num = 10 * num + 1
    return [[int(char) for char in data[num + i]] for i in range(9)]

class Stack():
    def __init__(self):
        self.data = []

    def __str__(self):
        return str(self.data)

    def push(self, item):
        self.data.append(item)

    def pop(self):
        if len(self.data) >= 1:
            return self.data.pop()
        return None

# print("Welcome to sudoku!")
# b = sudoku.Board(generateBoard(int(input("Pick a board from 0 to 50: "))))
# print(b)
# print(b.isSolved())
# while not b.isSolved():
#     cmd = input(">> ")
#     if b.update(int(cmd[0]), int(cmd[2]), int(cmd[4])):
#         print(b)
# print("Congrats you solved it!")