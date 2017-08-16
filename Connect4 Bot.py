import socket
import random
import time
import copy

from pprint import pprint

TCP_IP = '127.0.0.1'
#TCP_PORT = int(input("Port: "))
TCP_PORT = 4000
isPlaying = True

#Buffer for the incoming messages, very unlikely it will ever surpass 1024!
BUFFER_SIZE = 1024

NUM_ROW = 6
NUM_COL = 7

DELAY = 0
DEPTH = 4

OPPONENT = -1
ME = 1

test_board_row = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0],
]
test_board_diag = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
]
test_board_col = [
    [0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
]
test_board_col2 = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
]
test_board_col_opp = [
    [+1, +1, +0, +0, +0, +0, +0], 
    [-1, +1, +0, +0, +0, +0, +0],
    [+1, +1, -1, +0, +0, +0, +0],
    [+1, -1, -1, +0, +0, +0, +0],
    [-1, +1, -1, +0, +0, +0, +0],
    [+1, -1, -1, -1, +1, +0, +0],
]
test_board_row_opp = [
    [+1, +1, +0, +0, +0, +0, +0], 
    [-1, +1, +0, +0, +0, +0, +0],
    [+1, +1, -1, +0, +0, +0, +0],
    [+1, -1, -1, -1, -1, +0, +0],
    [-1, +1, -1, +0, +0, +0, +0],
    [+1, -1, -1, -1, +1, +0, +0],
]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
#Checks messages until it receives "GameOver"
#Always responds with a random move
def main():
    #Connects using TCP to localIP and specified Port
    last_board = []
    for i in range(NUM_ROW):
        last_board.append([0] * NUM_COL)

    while isPlaying:
        data = s.recv(BUFFER_SIZE)
        if data == "GameOver":
            break

        message = list(map(int, data.decode("utf-8").split()))
        board = make_board(message)
        #pprint(board)

        
        # Default move middle
        next_move = 3
        move_pos = get_move_position(last_board, board)
        if move_pos != None:
            if move_pos[1] in available_moves: 
                next_move = move_pos[1]
            else:
                #next_move = random.choice(available_moves)
                next_move = available_moves[0]

        available_moves = get_available_moves(board)
        next_move = minimax(board)
        #print("AFTER MINIMAX move is {}".format(next_move))

        time.sleep(DELAY)
        last_board = board

        msg = str(next_move)

        s.send(bytes(msg, "utf-8"))
        input()

#Closes connection when we are done
    s.close()

def get_move_position(last_board, board):
    for row in range(NUM_ROW):
        if last_board[row] != board[row]:
            for col in range(NUM_COL):
                if last_board[row][col] == 0 and board[row][col] == -1:
                    #print("Diff at row {} col {}".format(i, j))
                    return((row, col))

def get_available_moves(board):
    available_moves = []
    for i in range(NUM_COL):
        if board[0][i] == 0:
            available_moves.append(i)
    #print(available_moves)
    return available_moves

def make_board(message):
    board = []
    for i in range(NUM_COL):
        board.append(message[i*6 : (i+1)*6])
    # Transpose
    return list(map(list, list(zip(*board))))

def print_board(board):
    for row in board:
        print(("{:<+} "*NUM_COL).format(*row))

def find_threat_row(board):
    rows_start_pos = []
    for row in range(NUM_ROW):
        for col in range(NUM_COL-3):
            if (board[row][col] == -1) and (board[row][col+1] == -1) and (board[row][col+2] == -1):
                #print("row of three row {} col {} to {}".format(row, col, col+2))
                rows_start_pos.append((row, col))
    
def has_won_row(board, PLAYER):
    return _has_won_line(board, NUM_ROW, NUM_COL, PLAYER)

def has_won_col(board, PLAYER):
    transpose = list(zip(*copy.deepcopy(board)))
    for col in range(NUM_COL):
        for row in range(NUM_ROW-3):
            seq_len = 0
            for i in range(4):
                if board[row+i][col] == PLAYER:
                    seq_len += 1
            if seq_len == 4:
                return True
    return False

def _has_won_line(board, num_rows, num_cols, PLAYER):
    for row in range(num_rows):
        for col in range(num_cols-3):
            seq_len = 0
            for i in range(4):
                if board[row][col+i] == PLAYER:
                    seq_len += 1
            if seq_len == 4:
                return True
    return False

def has_won_diag(board, PLAYER):
    def is_diag_win(row, col, direction):
        seq_len = 0
        for i in range(4):
            if board[row + i][col + i*direction] == PLAYER:
                seq_len += 1
        if seq_len == 4:
            return True

    DOWN_LEFT = -1
    DOWN_RIGHT = 1
    for col in range(4):
        for row in range(3):
            if is_diag_win(row, col, DOWN_RIGHT):
                return True
    for col in range(3, NUM_COL):
        for row in range(3):
            if is_diag_win(row, col, DOWN_LEFT):
                return True
    return False


def has_won(board, PLAYER):
    return has_won_col(board, PLAYER) or has_won_row(board, PLAYER) or has_won_diag(board, PLAYER)


def simulate_move(board, move, PLAYER):
    new_board = copy.deepcopy(board)
    #print("BEFORE SIMULATION PLAYER {}".format(PLAYER))
    #print_board(new_board)
    for row in range(5, -1, -1):
        #print("Check row {}".format(row))
        if new_board[row][move] == 0:
            new_board[row][move] = PLAYER
            break
    #print("AFTER SIMULATION MOVE {} row {} PLAYER {}".format(move, row, PLAYER))
    #print_board(new_board)
    return new_board

def minimax(board):
    moves = get_available_moves(board)
    best_move = moves[0]
    best_score = float('-inf')
    scores = []
    for move in moves:
        #print("CHECKING MOVE {}".format(move))
        new_board = simulate_move(board, move, ME)
        #print_board(new_board)
        score = min_play(new_board, 1)
        scores.append(score)
        #print("Score from min play move {} score {}".format(move, score))
        if score > best_score:
            #print("Bettter score {}".format(score))
            best_move = move
            best_score = score
        #elif score == best_score:
            #best_move = random.choice((move, best_move))
            #print("Same score, taking random move {}".format(best_move))
        #input()
    #print("BEST MOVE CHOSEN {}".format(best_move))
    #print("MINIMAX scores {}".format(scores))
    return best_move
        

def min_play(board, depth):
    #print("MIN play LOOK HERE")
    #print_board(board)
    if has_won(board, OPPONENT):
        #print("MIN WON depth {}, return -1".format(depth))
        return -1
    if has_won(board, ME):
        #print("MAX WON depth {}, return 1".format(depth))
        return 1
    if depth == DEPTH:
        return 0
    scores = []
    moves = get_available_moves(board)
    for move in moves:
        #print("Min play move {}".format(move))
        next_board = simulate_move(board, move, OPPONENT)
        score = max_play(next_board, depth+1)
        #print("MIN depth {} simulated move:".format(depth))
        #print_board(next_board)
        #print("Score {}".format(score))
        scores.append(score)
    #print("Min play depth {} max scores {}".format(depth, scores))
    return min(scores)

def max_play(board, depth):
    #print("MAX play")
    #print_board(board)
    if has_won(board, OPPONENT):
        #print("MIN WON depth {}, return -1".format(depth))
        return -1
    if has_won(board, ME):
        #print("MAX WON depth {}, return 1".format(depth))
        return 1
    if depth == DEPTH:
        return 0
    scores = []
    moves = get_available_moves(board)
    for move in moves:
        next_board = simulate_move(board, move, ME)
        score = min_play(next_board, depth+1)
        #print("Max depth {} simulated move {} score {}:".format(depth, move, score))
        #print_board(next_board)
        #print("Score {}".format(score))
        scores.append(score)
    #print("MAX play depth {} scores {}".format(depth, scores))
    return max(scores)

if __name__ == '__main__':
    assert has_won_row(test_board_row, ME)
    assert has_won_col(test_board_col, ME)
    assert has_won_col(test_board_col2, ME)
    assert has_won_diag(test_board_diag, ME)
    assert has_won_row(test_board_row_opp, OPPONENT)
    assert has_won_col(test_board_col_opp, OPPONENT)
    main()
