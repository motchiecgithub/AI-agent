# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent
import numpy as np
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from .board import *
import time
from collections import defaultdict
# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!

class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        self.time = time.time()
        self.board = Board()
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")
    def minimax(self, depth: int, alpha, beta, turn: bool):
        # reach leaf node 
        if depth == 0:
            return self.evaluate()
        moves = self.generate_moves()
        if turn: 
            # maximize move 
            best_eval = -np.inf
            for move in moves:
                self.board.apply_action(move)
                evaluation = self.minimax(depth -1, alpha, beta, False)
                best_eval = max(best_eval, evaluation)
                alpha = max(alpha, evaluation)
                self.board.undo_action()
                if (beta <= alpha):
                    break
            return best_eval
        else:
            # minimize move
            best_eval = np.inf
            for move in moves:
                self.board.apply_action(move)
                evaluation = self.minimax(depth -1, alpha, beta, True)
                best_eval = min(best_eval, evaluation)
                beta = min(beta, evaluation)
                self.board.undo_action()
                if beta <= alpha:
                    break
            return best_eval
    def evaluate(self):
        red = self.board._color_power(PlayerColor.RED)
        blue = self.board._color_power(PlayerColor.BLUE)
        evaluation = red - blue 
        turn = 1
        if self.board._turn_color == PlayerColor.BLUE:
            turn = -1
        return evaluation * turn
    def generate_moves(self):
        if (self.board._total_power >=49 or not self.spawn_node()):
            return self.capture_node()
        return self.capture_node() +  self.spawn_node()
    def spawn_node(self):
        danger_zone = self.protected_zone(self.board.turn_color.opponent)
        color = self.board.turn_color
        for item in self.board._state:
            if self.board._state[item].player == color: 
                for dir in HexDir:
                    coor = item + dir 
                    if (not self.board._state.get(coor) or
                        self.board._state[coor].player == None):
                        if danger_zone[coor] == 1:
                            return [SpawnAction(coor)]
                        
        # spawn outside range of opponent
        for item in self.board._state:
            # check for opponent 
            if (self.board._state[item].player != None and 
                self.board._state[item].player != color):
                for dir in HexDir:
                    # check if spawn is legal 
                    coor = item + dir * (self.board._state[item].power + 1)
                    if (not self.board._state.get(coor) or
                        self.board._state[coor].player == None):
                        return [SpawnAction(coor)]
    def capture_node(self):
        # capture adjacent opponent
        color = self.board.turn_color
        moves = []
        player = {}
        opponent = {}
        # seperate player and opponent
        for item in self.board._state:
            if self.board._state[item].player == color:
                player[item] = self.board._state[item]
            elif self.board._state[item].player != None: 
                opponent[item] = self.board._state[item]

        # check for adjacent opponent and capture 
        for node in player:
            for dir in HexDir:
                found = 0
                for power in range(1, player[node].power + 1):
                    if found:
                        break
                    if (node + dir * power) in opponent:
                        moves.append(SpreadAction(node, dir))
                        found = 1
        return moves
    
    def protected_zone(self, color: PlayerColor):
        """
        return the zone where the player can spawn a protected piece
        a protected piece is a piece which is protected by other piece 
        this is also a danger zone for the opponent
        """
        protected = defaultdict(int)
        board = self.board._state
        for item in board:
            if board[item].player == color:
                for power in range(1, board[item].power + 1):
                    for dir in HexDir:
                        protected[item + dir * power] += 1
        return protected
    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        depth = 9
        time_remaining = referee['time_remaining']
        if (time_remaining > 150):
            depth = 9
        elif (time_remaining > 120):
            depth = 7
        elif (time_remaining > 60):
            depth = 5
        elif (time_remaining > 10):
            depth = 3
        else:
            depth = 1
        print(depth)
        match self._color:
            case PlayerColor.BLUE:
                if (not self.board._state):
                    return SpawnAction(HexPos(3,3))
                moves = self.generate_moves() # blue's move 
                best_eval = -np.inf
                for move in moves:
                    self.board.apply_action(move)
                    eval = self.minimax(depth, -np.inf, np.inf, False)
                    if (eval > best_eval):
                        best_eval = eval
                        best_move = move
                    self.board.undo_action()

                return best_move

            case PlayerColor.RED:
                if (not self.board._state):
                    return SpawnAction(HexPos(3,3))
                moves = self.generate_moves() 
                best_move = None
                best_eval = -np.inf
                for move in moves:
                    self.board.apply_action(move)
                    eval = self.minimax(depth, -np.inf, np.inf, False)
                    if (eval > best_eval):
                        best_eval = eval
                        best_move = move
                    self.board.undo_action()
                print(time.time() - self.time)
                return best_move

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        self.board.apply_action(action)
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass
