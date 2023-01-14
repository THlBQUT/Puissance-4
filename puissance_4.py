import tkinter as tk
from tkinter import ttk
import numpy as np
import random as rnd
from threading import Thread
from queue import Queue

disk_color = ['white', 'red', 'orange']
disks = list()

player_type = ['human']
for i in range(42):
    player_type.append('AI: alpha-beta level ' + str(i + 1))


def alpha_beta_decision(board, turn, ai_level, queue, max_player):
    explored_nodes = 0
    possible_moves = board.get_possible_moves()
    best_move = possible_moves[0]
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    explored_nodes += len(possible_moves)
    for move in possible_moves:
        explored_nodes += 1
        updated_board = board.copy()
        updated_board.add_disk(move, max_player, False)

        value = minmax(updated_board, ai_level, turn, alpha, beta, game.current_player())
        if value > best_value:
            best_value = value
            best_move = move
        alpha = max(alpha, best_value)
    print("EXPLORED NODES : ", explored_nodes)
    print("BEST VALUE : ", best_value)
    queue.put(best_move)


def min_value_alpha_beta(board, turn, alpha, beta, max_player, explored_nodes, max_recursion):
    if board.check_victory():
        return -200, explored_nodes

    elif turn > max_recursion:
        return 0, explored_nodes

    possible_moves = board.get_possible_moves()
    value = 2000000

    for move in possible_moves:
        explored_nodes += 1
        updated_board = board.copy()
        updated_board.add_disk(move, max_player, False)
        max_val, explored_nodes = max_value_alpha_beta(updated_board, turn + 1, alpha, beta, 2 - ((max_player + 1) % 2),
                                                       explored_nodes, max_recursion)
        value = min(value, max_val)
        if value <= alpha:
            return value, explored_nodes
        beta = min(beta, value)
    return value, explored_nodes


def max_value_alpha_beta(board, turn, alpha, beta, max_player, explored_nodes, max_recursion):
    if board.check_victory():
        return -200, explored_nodes

    elif turn > max_recursion:
        return 0, explored_nodes

    possible_moves = board.get_possible_moves()
    value = -2000000

    for move in possible_moves:
        explored_nodes += 1
        updated_board = board.copy()
        updated_board.add_disk(move, max_player, False)
        min_val, explored_nodes = min_value_alpha_beta(updated_board, turn + 1, alpha, beta, 2 - ((max_player + 1) % 2),
                                                       explored_nodes, max_recursion)
        value = max(value, min_val)
        if value >= beta:
            return value, explored_nodes
        alpha = max(alpha, value)
    return value, explored_nodes


def minmax(board, depth, turn, alpha, beta, max_player):
    if depth == 0 or board.check_victory():
        return board.eval(max_player, turn)

    if max_player == 1:
        best_score = float('-inf')
        for move in board.get_possible_moves():
            new_board = board.copy()
            new_board.add_disk(move, max_player, False)
            score = minmax(new_board, depth - 1, turn, alpha, beta, game.current_player())
            best_score = max(score, best_score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = float('inf')
        for move in board.get_possible_moves():
            new_board = board.copy()
            new_board.add_disk(move, max_player, False)
            score = minmax(new_board, depth - 1, turn, alpha, beta, game.current_player())
            best_score = min(score, best_score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score


class Board:
    grid = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])

    def eval(self, player, turn):
        if player == 1:
            return 0
        else:
            opponent = 1

        # Les méthodes count_fours, count_threes et count_twos
        # vont définir notre heuristique

        player_fours = self.count_fours(player)
        opponent_fours = self.count_fours(opponent)

        player_threes = self.count_threes(player)
        opponent_threes = self.count_threes(opponent)

        player_twos = self.count_twos(player)
        opponent_twos = self.count_twos(opponent)

        return \
            player_fours + player_threes + player_twos\
                - (opponent_fours * 5 + opponent_threes * 1.5 + opponent_twos)

    def copy(self):
        new_board = Board()
        new_board.grid = np.array(self.grid, copy=True)
        return new_board

    def reinit(self):
        self.grid.fill(0)
        for i in range(7):
            for j in range(6):
                canvas1.itemconfig(disks[i][j], fill=disk_color[0])

    def get_possible_moves(self):
        possible_moves = list()
        if self.grid[3][5] == 0:
            possible_moves.append(3)
        for shift_from_center in range(1, 4):
            if self.grid[3 + shift_from_center][5] == 0:
                possible_moves.append(3 + shift_from_center)
            if self.grid[3 - shift_from_center][5] == 0:
                possible_moves.append(3 - shift_from_center)
        return possible_moves

    def add_disk(self, column, player, update_display=True):
        for j in range(6):
            if self.grid[column][j] == 0:
                break
        self.grid[column][j] = player
        if update_display:
            canvas1.itemconfig(disks[column][j], fill=disk_color[player])

    def column_filled(self, column):
        return self.grid[column][5] != 0

    def check_victory(self):
        # Horizontal alignment check
        for line in range(6):
            for horizontal_shift in range(4):
                if self.grid[horizontal_shift][line] == self.grid[horizontal_shift + 1][line] == \
                        self.grid[horizontal_shift + 2][line] == self.grid[horizontal_shift + 3][line] != 0:
                    return True
        # Vertical alignment check
        for column in range(7):
            for vertical_shift in range(3):
                if self.grid[column][vertical_shift] == self.grid[column][vertical_shift + 1] == \
                        self.grid[column][vertical_shift + 2] == self.grid[column][vertical_shift + 3] != 0:
                    return True
        # Diagonal alignment check
        for horizontal_shift in range(4):
            for vertical_shift in range(3):
                if self.grid[horizontal_shift][vertical_shift] == self.grid[horizontal_shift + 1][vertical_shift + 1] == \
                        self.grid[horizontal_shift + 2][vertical_shift + 2] == self.grid[horizontal_shift + 3][
                        vertical_shift + 3] != 0:
                    return True
                elif self.grid[horizontal_shift][5 - vertical_shift] == self.grid[horizontal_shift + 1][
                        4 - vertical_shift] == \
                        self.grid[horizontal_shift + 2][3 - vertical_shift] == self.grid[horizontal_shift + 3][
                        2 - vertical_shift] != 0:
                    return True
        return False

    def count_fours(self, player):
        fours = 0

        # Horizontal
        for line in range(6):
            for column in range(4):
                if column + 3 < 7 \
                        and self.grid[column][line] == player \
                        and self.grid[column + 1][line] == player \
                        and self.grid[column + 2][line] == player \
                        and self.grid[column + 3][line] == player:
                    fours += 1

        # Vertical
        for line in range(3):
            for column in range(7):
                if self.grid[column][line] == player \
                        and self.grid[column][line + 1] == player \
                        and self.grid[column][line + 2] == player \
                        and self.grid[column][line + 3] == player:
                    fours += 1

        # Diagonale
        for line in range(3):
            for column in range(4):
                if column + 3 < 7 \
                        and self.grid[column][line] == player \
                        and self.grid[column + 1][line + 1] == player \
                        and self.grid[column + 2][line + 2] == player \
                        and self.grid[column + 3][line + 3] == player:
                    fours += 1

        # Diagonale inverse
        for line in range(3, 6):
            for column in range(7):
                if column + 3 < 7 \
                        and self.grid[column][line] == player \
                        and self.grid[column + 1][line - 1] == player \
                        and self.grid[column + 2][line - 2] == player \
                        and self.grid[column + 3][line - 3] == player:
                    fours += 1

        return fours

    def count_threes(self, player):
        threes = 0

        # Horizontal
        for line in range(6):
            for column in range(6):
                if column + 2 < 7 \
                        and self.grid[column][line] == player \
                        and self.grid[column + 1][line] == player \
                        and self.grid[column + 2][line] == player:
                    threes += 1

        # Vertical
        for line in range(4):
            for column in range(7):
                if self.grid[column][line] == player \
                        and self.grid[column][line + 1] == player \
                        and self.grid[column][line + 2] == player:
                    threes += 1

        # Diagonale
        for line in range(4):
            for column in range(6):
                if column + 2 < 7 \
                        and self.grid[column][line] == player \
                        and self.grid[column + 1][line + 1] == player \
                        and self.grid[column + 2][line + 2] == player:
                    threes += 1

        # Diagonale inverse
        for line in range(2, 6):
            for column in range(6):
                if column + 2 < 7 \
                        and self.grid[column][line] == player \
                        and self.grid[column + 1][line - 1] == player \
                        and self.grid[column + 2][line - 2] == player:
                    threes += 1

        return threes

    def count_twos(self, player):
        twos = 0

        # Horizontal
        for line in range(6):
            for column in range(5):
                if column + 1 < 7 \
                        and self.grid[column][line] == player \
                        and self.grid[column + 1][line] == player:
                    twos += 1

        # Vertical
        for line in range(5):
            for column in range(7):
                if self.grid[column][line] == player \
                        and self.grid[column][line + 1] == player:
                    twos += 1

        # Diagonale
        for line in range(5):
            for column in range(5):
                if column + 1 < 7 \
                        and self.grid[column][line] == player \
                        and self.grid[column + 1][line + 1] == player:
                    twos += 1

        # Diagonale inverse
        for line in range(1, 6):
            for column in range(5):
                if column + 1 < 7 \
                        and self.grid[column][line] == player \
                        and self.grid[column + 1][line - 1] == player:
                    twos += 1

        return twos


class Connect4:

    def __init__(self):
        self.board = Board()
        self.human_turn = False
        self.turn = 1
        self.players = (0, 0)
        self.ai_move = Queue()

    def current_player(self):
        return 2 - (self.turn % 2)

    def launch(self):
        self.board.reinit()
        self.turn = 0
        information['fg'] = 'black'
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        self.human_turn = False
        self.players = (combobox_player1.current(), combobox_player2.current())
        self.handle_turn()

    def move(self, column):
        if not self.board.column_filled(column):
            self.board.add_disk(column, self.current_player())
            self.handle_turn()

    def click(self, event):
        print(self.current_player())
        if self.human_turn:
            column = event.x // row_width
            self.move(column)

    def ai_turn(self, ai_level):
        Thread(target=alpha_beta_decision,
               args=(self.board, self.turn, ai_level, self.ai_move, self.current_player(),)).start()
        self.ai_wait_for_move()

    def ai_wait_for_move(self):
        if not self.ai_move.empty():
            self.move(self.ai_move.get())
        else:
            window.after(100, self.ai_wait_for_move)

    def handle_turn(self):
        self.human_turn = False
        if self.board.check_victory():
            information['fg'] = 'red'
            information['text'] = "Player " + str(self.current_player()) + " wins !"
            return
        elif self.turn >= 42:
            information['fg'] = 'red'
            information['text'] = "This a draw !"
            return
        self.turn = self.turn + 1
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        if self.players[self.current_player() - 1] != 0:
            self.human_turn = False
            print(self.players)
            self.ai_turn(self.players[self.current_player() - 1])
        else:
            self.human_turn = True


game = Connect4()

# Graphical settings
width = 600
row_width = width // 7
row_height = row_width
height = row_width * 6
row_margin = row_height // 10

window = tk.Tk()
window.title("Connect 4")
canvas1 = tk.Canvas(window, bg="blue", width=width, height=height)

# Drawing the grid
for i in range(7):
    disks.append(list())
    for j in range(5, -1, -1):
        disks[i].append(canvas1.create_oval(row_margin + i * row_width, row_margin + j * row_height,
                                            (i + 1) * row_width - row_margin,
                                            (j + 1) * row_height - row_margin, fill='white'))

canvas1.grid(row=0, column=0, columnspan=2)

information = tk.Label(window, text="")
information.grid(row=1, column=0, columnspan=2)

label_player1 = tk.Label(window, text="Player 1: ")
label_player1.grid(row=2, column=0)
combobox_player1 = ttk.Combobox(window, state='readonly')
combobox_player1.grid(row=2, column=1)

label_player2 = tk.Label(window, text="Player 2: ")
label_player2.grid(row=3, column=0)
combobox_player2 = ttk.Combobox(window, state='readonly')
combobox_player2.grid(row=3, column=1)

combobox_player1['values'] = player_type
combobox_player1.current(0)
combobox_player2['values'] = player_type
combobox_player2.current(6)

button2 = tk.Button(window, text='New game', command=game.launch)
button2.grid(row=4, column=0)

button = tk.Button(window, text='Quit', command=window.destroy)
button.grid(row=4, column=1)

# Mouse handling
canvas1.bind('<Button-1>', game.click)

window.mainloop()
