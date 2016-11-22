import copy
import sys


def read_input():
    f = open("input.txt", 'r')
    line = f.readline()
    lines = []
    while line:
        line = line.strip()
        if line:
            lines.append(line)
        line = f.readline()
    f.close()
    return lines


def process_input(input_file):
    global N
    global cutoff
    global mode
    global player1
    global player2
    global cell
    global board
    N = int(input_file[0])
    mode = input_file[1]
    you_play = input_file[2]
    cutoff = int(input_file[3])
    curent_index = 4
    cell = []
    board = []
    for i in range(0, N):
        cell_row = input_file[curent_index].split(" ")
        curent_index += 1
        cell.append(cell_row)

    for j in range(0, N):
        board_row = input_file[curent_index]
        curent_index += 1
        board.append(list(board_row))

    if you_play == "X":
        player1 = "X"
        player2 = "O"
    else:
        player1 = "O"
        player2 = "X"


def is_end_game(state):
    for i in range(0, N):
        for j in range(0, N):
            if state[i][j] == ".":
                return False
    return True


def evaluation(state):
    score = 0
    for i in range(0, N):
        for j in range(0, N):
            if state[i][j] == player1:
                score += int(cell[i][j])
            elif state[i][j] == player2:
                score -= int(cell[i][j])
    return score


def move(state, i, j, player):
    temp_state = copy.deepcopy(state)
    temp_state[i][j] = player
    return temp_state


def move_raid(state, i, j, player):

    temp_state = copy.deepcopy(state)
    temp_state[i][j] = player
    neighbor_self = False
    if player == "X":
        oppent = "O"
    else:
        oppent = "X"

    up = ""
    left = ""
    down = ""
    right = ""

    if i != 0:
        up = temp_state[i - 1][j]
    if j != 0:
        left = temp_state[i][j - 1]
    if i != N - 1:
        down = temp_state[i + 1][j]
    if j != N - 1:
        right = temp_state[i][j + 1]

    if up == player or down == player or left == player or right == player:
        neighbor_self = True

    if neighbor_self:
        if up == oppent:
            temp_state[i - 1][j] = player
        if left == oppent:
            temp_state[i][j - 1] = player
        if down == oppent:
            temp_state[i + 1][j] = player
        if right == oppent:
            temp_state[i][j + 1] = player

    return temp_state


def check_raid(state, i, j, player):
    temp_state = copy.deepcopy(state)
    temp_state[i][j] = player
    neighbor_self = False
    can_raid = False
    if player == "X":
        oppent = "O"
    else:
        oppent = "X"

    up = ""
    left = ""
    down = ""
    right = ""

    if i != 0:
        up = temp_state[i - 1][j]
    if j != 0:
        left = temp_state[i][j - 1]
    if i != N - 1:
        down = temp_state[i + 1][j]
    if j != N - 1:
        right = temp_state[i][j + 1]

    if up == player or down == player or left == player or right == player:
        neighbor_self = True

    if neighbor_self:
        if up == oppent:
            can_raid = True
        if left == oppent:
            can_raid = True
        if down == oppent:
            can_raid = True
        if right == oppent:
            can_raid = True

    return can_raid


def minmax(state, player, current_depth):
    global final_board_state

    if is_end_game(state) or current_depth >= cutoff:
        return evaluation(state)
    if current_depth != 0:
        player = switch_player(player)

    raids = []
    for a in range(0, N):
        for b in range(0, N):
            if state[a][b] == ".":
                if check_raid(state, a, b, player):
                    raids.append([a, b])

    if player == player1:
        max_score = -sys.maxint + 1
        for i in range(0, N):
            for j in range(0, N):
                if state[i][j] == ".":
                    next_board = move(state, i, j, player)
                    value = minmax(next_board, player, current_depth + 1)
                    if value > max_score:
                        max_score = value
                        if current_depth == 0:
                            final_board_state = copy.deepcopy(next_board)

        for raid in raids:
            next_board = move_raid(state, raid[0], raid[1], player)
            value = minmax(next_board, player, current_depth + 1)
            if value > max_score:
                max_score = value
                if current_depth == 0:
                    final_board_state = copy.deepcopy(next_board)
        return max_score
    else:
        min_score = sys.maxint
        for i in range(0, N):
            for j in range(0, N):
                if state[i][j] == ".":
                    next_board = move(state, i, j, player)
                    value = minmax(next_board, player, current_depth + 1)
                    if value < min_score:
                        min_score = value

        for raid in raids:
            next_board = move_raid(state, raid[0], raid[1], player)
            value = minmax(next_board, player, current_depth + 1)
            if value < min_score:
                min_score = value
        return min_score


def switch_player(player):
    if player == 'X':
        player = 'O'
    else:
        player = 'X'

    return player


def locate_next_move(state):
    for i in range(0, N):
        for j in range(0, N):
            if state[i][j] == player1 and board[i][j] == ".":
                return i, j
    return -1, -1


def next_move(state):
    move = locate_next_move(state)
    return chr(move[1]+65) + str(move[0] + 1)


def alphabeta(state, player, current_depth, alpha, beta):
    global final_board_state

    if is_end_game(state) or current_depth >= cutoff:
        return evaluation(state)
    if current_depth != 0:
        player = switch_player(player)

    raids = []
    for a in range(0, N):
        for b in range(0, N):
            if state[a][b] == ".":
                if check_raid(state, a, b, player):
                    raids.append([a, b])

    if player == player1:
        max_score = -sys.maxint + 1
        for i in range(0, N):
            for j in range(0, N):
                if state[i][j] == ".":
                    next_board = move(state, i, j, player)
                    value = alphabeta(next_board, player, current_depth + 1, alpha, beta)
                    if value > max_score:
                        max_score = value
                        if current_depth == 0:
                            final_board_state = copy.deepcopy(next_board)
                    alpha = max(alpha, max_score)
                    if beta <= alpha:
                        return beta
        for raid in raids:
            next_board = move_raid(state, raid[0], raid[1], player)
            value = alphabeta(next_board, player, current_depth + 1, alpha, beta)
            if value > max_score:
                max_score = value
                if current_depth == 0:
                    final_board_state = copy.deepcopy(next_board)
            alpha = max(alpha, max_score)
            if beta <= alpha:
                return beta
        return alpha
    else:
        min_score = sys.maxint
        for i in range(0, N):
            for j in range(0, N):
                if state[i][j] == ".":
                    next_board = move(state, i, j, player)
                    value = alphabeta(next_board, player, current_depth + 1, alpha, beta)
                    if value < min_score:
                        min_score = value
                    beta = min(beta, min_score)
                    if beta <= alpha:
                        return alpha
        for raid in raids:
            next_board = move_raid(state, raid[0], raid[1], player)
            value = alphabeta(next_board, player, current_depth + 1, alpha, beta)
            if value < min_score:
                min_score = value
            beta = min(beta, min_score)
            if beta <= alpha:
                return alpha
        return beta


def identify_type(state):
    diff = 0
    for i in range(0, N):
        for j in range(0, N):
            if state[i][j] != board[i][j]:
                diff += 1
    if diff > 1:
        return "Raid"
    else:
        return "Stake"


def write_output(state):
    out.write(next_move(state) + " " + identify_type(state) + "\n")
    for row in state:
        for each in row:
            out.write(str(each))
        out.write('\n')
    return


if __name__ == "__main__":
    input = read_input()
    process_input(input)
    out = open('output.txt', 'w')
    if mode == "MINIMAX":
        max = minmax(board, player1, 0)
        write_output(final_board_state)
    elif mode == "ALPHABETA":
        alpha_value = alphabeta(board, player1, 0, -sys.maxint + 1, sys.maxint)
        write_output(final_board_state)
    out.close()
