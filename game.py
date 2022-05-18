from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import time

# PART1 CREATING THE INTERFACE
# Using tkinter.canvas() to create a window with set dimension and background color.
inter = Tk()
inter.title(string="Gomoku with Eileen's rules")
window = Canvas(inter, width=750, height=1000, background="#bfbdb6")
window.pack()

# Setting basic properties of the chess board
board_size = 15
frame_gap = 35
width = 800
height = 800
x1 = width / 10
y1 = height / 10
x_gap = (width - x1 * 2) / board_size
y_gap = (height - y1 * 2) / board_size
chess_radius = (x_gap * (9 / 10)) / 2

# Define turns
rounds = 1
turn = "black"
winner = None
display = window.create_text(120, 780, text="Player: " + turn, font="Helvetica 25 bold", fill=turn)
black_turn = 1
white_turn = 0
flag = False

# Function that detects the coodinates where player clicks
def mouse_click(event):
    global Click_Cord
    x = event.x
    y = event.y
    X = None
    Y = None
    for i in range(len(Actual_CordX1)):
        if x > Actual_CordX1[i] and x < Actual_CordX2[i]:
            X = Game_CordX[i]
        if y > Actual_CordY1[i] and y < Actual_CordY2[i]:
            Y = Game_CordY[i]
    Click_Cord = (X, Y)


# Define/initiate coordinates
window.bind("<Button-1>", mouse_click)
Click_Cord = [None, None]

# Initiate variables
Game_CordX = []
Game_CordY = []
Actual_CordX1 = []
Actual_CordY1 = []
Actual_CordX2 = []
Actual_CordY2 = []
Black_Cord_PickedX = []
Black_Cord_PickedY = []
White_Cord_PickedX = []
White_Cord_PickedY = []

board = []

# PART2 HELPER FUNCTIONS
# Create the chess (gomoku) board.
def make_board():
    window.create_rectangle(x1 - frame_gap, y1 - frame_gap, x1 + frame_gap + x_gap * (board_size - 1), y1 + frame_gap
                            + y_gap * (board_size - 1), width=3)
    # Create lines
    for f in range(board_size):
        window.create_line(x1, y1 + f * y_gap, x1 + x_gap * (board_size - 1), y1 + f * y_gap)
        window.create_line(x1 + f * x_gap, y1, x1 + f * x_gap, y1 + y_gap * (board_size - 1))
        window.create_text(x1 - frame_gap * 1.7, y1 + f * y_gap, text=f + 1, font="Helvetica 10 bold", fill="black")
        window.create_text(x1 + f * x_gap, y1 - frame_gap * 1.7, text=f + 1, font="Helvetica 10 bold", fill="black")

    # Initiate board variable
    for i in range(board_size + 2):
        board.append([0] * (board_size + 2))

    # Initiate cord variables
    for z in range(1, board_size + 2):
        for i in range(1, board_size + 2):
            Game_CordX.append(z)
            Game_CordY.append(i)
            Actual_CordX1.append((z - 1) * x_gap + x1 - chess_radius)
            Actual_CordY1.append((i - 1) * y_gap + y1 - chess_radius)
            Actual_CordX2.append((z - 1) * x_gap + x1 + chess_radius)
            Actual_CordY2.append((i - 1) * y_gap + y1 + chess_radius)

# Displays which player gets to go next.
def display_text():
    if winner is None:
        return window.create_text(120, 780, text="Player: " + turn, font="Helvetica 25 bold", fill=turn)
    else:
        window.create_text(width / 2, height - frame_gap + 15, text=winner.upper() + " WINS!", font="Helvetica 25 bold",
                           fill=winner.lower())

# Visually create the chess(gomoku) pieces
def create_circle(x, y, radius, fill="", outline="black", width=1):
    window.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill, outline=outline, width=width)


def row_check(piece_number, b):
    for i in range(len(b)):
        if b[i].count(piece_number) >= 5:
            for z in range(len(b) - 3):
                conn = 0
                for c in range(5):
                    if b[i][z + c] == piece_number:
                        conn += 1
                    else:
                        break
                    if conn == 5:
                        return True


def get_col(l, col_num):
    lst = []
    for i in range(len(l)):
        lst.append(l[i][col_num])
    return lst


def get_diagonal_inc(l, dig_num):
    lst = []
    if dig_num <= len(l) - 1:
        index = 0
        for i in range(dig_num, -1, -1):
            lst.append(l[i][index])
            index += 1
        return lst
    else:
        index = dig_num - len(l) + 1
        for i in range(len(l) - 1, dig_num - len(l), -1):
            lst.append(l[i][index])
            index += 1
        return lst


def get_diagonal_dec(l, dig_num):
    lst = []
    if dig_num <= len(l) - 1:
        index = len(l) - 1
        for i in range(dig_num, -1, -1):
            lst.append(l[i][index])
            index -= 1
        return lst
    else:
        index = (len(l) * 2 - 2) - dig_num
        for i in range(len(l) - 1, dig_num - len(l), -1):
            lst.append(l[i][index])
            index -= 1
        return lst


def transpose(l, f):
    lst = []
    for i in range(len(l)):
        lst.append(f(l, i))
    return lst


def win_check(b):
    if turn == "white":
        piece_number = 1
        win = "black"
    elif turn == "black":
        piece_number = 2
        win = "white"
    if row_check(piece_number, b) \
            or row_check(piece_number, transpose(board, get_col)) \
            or row_check(piece_number, transpose(board, get_diagonal_inc)) \
            or row_check(piece_number, transpose(board, get_diagonal_dec)):
        return win


def switch_round():
    global black_turn
    global white_turn
    temp = black_turn
    black_turn = white_turn
    white_turn = temp


# New rule I introduced to this game: if dice index = 5, then the player gets to go again.
def roll_dice():
    global flag
    index = 0
    for ii in range(20):
        index = np.random.randint(1, 7)
        img = Image.open(str(index) + '.png')
        img = ImageTk.PhotoImage(img)
        window.create_image(653, 755, anchor=NW, image=img)
        window.update()
        time.sleep(0.05)
    if index == 5:
        flag = True
    return index

# PART3 DEFINE HOW THE GAME RUNS
make_board()
ind = roll_dice()
while True:
    # A visual 'animation' that rolls the dice.
    img = Image.open(str(ind) + '.png')
    img = ImageTk.PhotoImage(img)
    window.create_image(653, 755, anchor=NW, image=img)
    window.update()

    X = Click_Cord[0]
    Y = Click_Cord[1]

    if X is None or Y is None:
        continue
    elif board[Y - 1][X - 1] == 0:
        window.delete(display)

        # store the coordinates of the pieces for each player
        create_circle(x1 + x_gap * (X - 1), y1 + y_gap * (Y - 1), radius=chess_radius, fill=turn)
        if rounds % 2 == black_turn:
            Black_Cord_PickedX.append(X)
            Black_Cord_PickedY.append(Y)
            board[Y - 1][X - 1] = 1
            turn = "white"
            if flag:
                switch_round()
                turn = "black"
                flag = False

        elif rounds % 2 == white_turn:
            White_Cord_PickedX.append(X)
            White_Cord_PickedY.append(Y)
            board[Y - 1][X - 1] = 2
            turn = "black"
            if flag:
                switch_round()
                turn = "white"
                flag = False

        display = display_text()

        rounds = rounds + 1

        winner = win_check(board)

        if winner is not None:
            break

        ind = roll_dice()

for j in range(5):
    window.create_text(400, 400, text="Winner: " + winner, font="Helvetica 80 bold", fill="gold")
    window.update()
    time.sleep(1)