from dataclasses import dataclass
from enum import Enum, IntEnum
from time import sleep
import heapq
import connection
import json_parser

@dataclass
class Vector3:
    x: int
    y: int
    z: int
# example
# location = Location(x, y, z)

class Result(IntEnum):
    OKEY = 0,
    BAD_COMMAND = 1,
    ACCESS_DENIED = 2,
    INAPPROPRIATE_GAME_STATE = 3,
    TIMEOUT = 4,
    INTERNAL_SERVER_ERROR = 500

# Requests
login_request = b'\x01\x00\x00\x00\x10\x00\x00\x00{"name": "Tank"}'
logout_request = b'\x02\x00\x00\x00\x00\x00\x00\x00'
map_request = b'\x03\x00\x00\x00\x00\x00\x00\x00'
game_state_request = b'\x04\x00\x00\x00\x00\x00\x00\x00'
game_actions_request = b'\x05\x00\x00\x00\x00\x00\x00\x00'
turn_request = b'\x06\x00\x00\x00\x00\x00\x00\x00'

def data_to_json(data):
    json_string = data.decode('utf-8', 'ignore')
    start_index = json_string.find('{')
    json_data_str = json_string[start_index:]
    return json_data_str


def hex_distance(a, b):
    return (abs(a[0] - b[0]) + abs(a[0] + a[1] - b[0] - b[1]) + abs(a[1] - b[1])) // 2

# 0.1v pathfinding. One goal, no check for vehicles as obstacles. Star and goal are tuples.
# Given goal, returns the shortest path
def find_path(start, goal, game_state, max_iterations=100):
    directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1),
            (2, -1), (1, -2), (-1, -1), (-2, 0), (-1, 2), (1, 1),
            (2, 0), (2, -2), (0, -2), (-2, 1), (-2, 2), (0, 2)]
    open_list = []
    closed_set = set()
    g_costs = {}
    parents = {}
    shortest_path_length = float('inf')
    shortest_path = None

    # Initialize start node
    g_costs[start] = 0
    f_cost = hex_distance(start, goal)
    heapq.heappush(open_list, (f_cost, start))

    iterations = 0
    while open_list and iterations < max_iterations:
        _, current = heapq.heappop(open_list)

        if current == goal:
            # Reconstruct the path
            path = [current]
            while current in parents:
                current = parents[current]
                path.append(current)
            path.reverse()
            if len(path) < shortest_path_length:
                shortest_path_length = len(path)
                shortest_path = path

        closed_set.add(current)

        for direction in directions:
            neighbor = (current[0] + direction[0] , current[1] + direction[1] )
            if neighbor in closed_set:
                
                
                continue  # Skip if neighbor is an obstacle or already visited
            # Skip if neighbor is occupied by another vehicle
            if taken(neighbor, game_state) and neighbor != goal:
                continue

            tentative_g_cost = g_costs[current] + 1 
            if neighbor not in g_costs or tentative_g_cost < g_costs[neighbor]:
                g_costs[neighbor] = tentative_g_cost
                f_cost = tentative_g_cost + hex_distance(neighbor, goal)
                heapq.heappush(open_list, (f_cost, neighbor))
                parents[neighbor] = current
        iterations += 1
                    # Calculate distance to the current goal and update closest goal if needed
    return shortest_path


    
# Checks if the hex is taken by another vehicle
def taken(hex, game_state):
    for vehicle in game_state.vehicles:
        if game_state.vehicles[vehicle].position.x == hex[0] and game_state.vehicles[vehicle].position.y == hex[1]:
            return True
    return False

# instance of game being played
class Game:
    def __init__(self, name):
        self.name = name
        self.idx = 0
        self.vehicles = []
        self.state = GameState()
        self.map = GameMap()
        self.controller = AIController(self)
        self.stop = False
        self.server = connection.ServerConnection('http://wgforge-srv.wargaming.net', 443)
        #init network component

    # I think it's only called once
    def init_map(self):
        data = self.server.send_request(map_request)
        assert(self.response_result(data) == Result.OKEY)
        json_data_str = data_to_json(data)
        self.map = json_parser.GameMapJsonDecoder(json_data_str)

    def game_loop(self):
        self.server.connect()
        self.login()
        self.init_map()
        self.update_game_state()

        while not self.stop:
            sleep(1) # I guess some sleep?

            self.update_game_state()

            if self.state.finished:
                self.stop = True
                self.logout()
                print("Game finished")
                print("Winner:", self.state.winner)
                print("Win points:", self.state.win_points)
                                
                self.print_vehicle_positions()
                break

            self.print_vehicle_positions()
            # maybe get game turns

            if self.is_clients_turn():
                
                # removed block debug 5
                # # Check if all vehicles are in their final position
                # all_in_place = all(abs(vehicle.position.x) < 2 and abs(vehicle.position.y) < 2 and abs(vehicle.position.z) < 2 for vehicle in self.vehicles)

                # # Skip loop iteration if all vehicles are in place
                # if all_in_place:
                #     self.skip_turn() # should be turned into an action?
                #     print("Skipping turn")
                #     continue

                for vehicle_id, vehicle in self.state.vehicles.items():
                    action = self.controller.get_game_action(vehicle_id, vehicle)
                    self.make_action(action)
                    print("moving vehicle", vehicle_id, vehicle.position, " to", action.target)
                self.skip_turn()

            # maybe end turn here

    def print_vehicle_positions(self):
        for vehicle_index in self.state.vehicles:
            print(self.state.vehicles[vehicle_index].position)
        print("\n")

    def skip_turn(self):
        data = self.server.send_request(turn_request)

    
    def update_game_state(self):
        data = self.server.send_request(game_state_request)
        assert(self.response_result(data) == Result.OKEY)
        json_data_str = data_to_json(data)
        self.state = json_parser.GameStateJsonDecoder(json_data_str)

    def is_clients_turn(self):
        return self.state.current_player_idx == self.idx

    def make_action(self, action):
        if(action.target is not None):
            move_action = MoveAction(self.idx, action.vehicle_id, action.target) # temporary solution with action being only move
            json_str = json_parser.ActionEncodeJson(move_action)
            data = b'\x65\x00\x00\x00' + len(json_str).to_bytes(4, 'little') + json_str.encode('utf-8')
            res = self.server.send_request(data) # send move action

    def login(self): #remove name for now
        data = self.server.send_request(login_request)
        assert(self.response_result(data) == Result.OKEY)
        json_data_str = data_to_json(data)
        response = json_parser.LoginJsonDecoder(json_data_str)
        self.idx = response.player_id
        print("Logged in as player with id:", self.idx)


    def logout(self):
        data = self.server.send_request(logout_request)
        assert(self.response_result(data) == Result.OKEY)

    # get response result
    def response_result(self, data):
        result = data[:4]
        integer_value = int.from_bytes(result, byteorder='little')
        return Result(integer_value)


# Login response
class LoginResponse:
    def __init__(self, player_id, name, is_observer):
        self.player_id = player_id
        self.name = name
        self.is_observer = is_observer

# game state
# for more info look at documentation, GameState Response
# all data about current game
class GameState:
    def __init__(self):
        self.num_players = 0
        self.num_turns = 0
        self.num_rounds = 0
        self.current_turn = 0
        self.current_round = 0
        self.players = []

        self.observers = []
        self.current_player_idx = 0
        self.finished = False
        self.vehicles = dict()
        self.attack_matrix = dict() # key is player, value is list of player ids
        self.winner = None
        self.win_points = dict() # Key is player ind, value is tuple (capture, kill points)
        self.player_result_points = dict()
        self.catapult_usage = []

# game map
# for more info look at documentation, Map Response
# all data about game entity locations
class GameMap:
    def __init__(self):
        self.name = None
        self.size = 0
        self.spawn_points = [] # !!!! IMPORTANT, this is list of json dict (if you need locations of vehicles USE GAMESTATE)
        self.entity_map = dict()
        # ALL entities should go in entity_map
        # entity_map["base"] returns list of locations of bases
    
    def get_all_base(self):
        return self.entity_map["base"]
    def get_all_obstacles(self):
        return self.entity_map["obstacle"]
    def get_all_light_repair(self):
        return self.entity_map["light_repeair"]
    def get_all_hard_repair(self):
        return self.entity_map["hard_repair"]
    def get_all_catapults(self):
        return self.entity_map["catapult"]

# Player (client and others)
class Player:
    def __init__(self, idx, name, is_observer):
        self.name = name
        self.idx = idx
        self.is_observer = is_observer


# tells networking system what to send
class Controller:
    def __init__(self, game):
        self.game = game
    
    # return GameAction
    def get_game_action(self, vehicle):
        raise NotImplementedError("Child class must override this method")


# Reads Console Input
# ONLY OPTIONAL, We don't need to do it now
class ConsoleController(Controller):
    def __init__(self, game):
        super(ConsoleController, self).__init__(game)

    def get_input(self):
        pass

# Uses AI Behavior Algorithms to pass data to player
class AIController(Controller):
    def __init__(self, game):
        super(AIController, self).__init__(game)

    def make_decision(self):
        pass

    def get_game_action(self, id, vehicle): # no smart decisions for now
        position = (vehicle.position.x, vehicle.position.y) #questionable?
        base_position = (self.game.map.get_all_base()[0].x, self.game.map.get_all_base()[0].y)
        #base_position = (0, 0)
        path = find_path(position, base_position, self.game.state)

        if path.__len__() < 2:
            target = position
        else:
            target = path[1]

        target_good = Vector3(target[0], target[1], -1*(target[0] + target[1]))
        return MoveAction(vehicle.player_id, id, target_good)

# Base class for all vehicles OR all vehicles if there is no need to make more classes
class Vehicle:
    def __init__(self):
        self.player_id = 0
        self.vehicle_type = None # enum or string
        self.health = 1
        self.spawn_position = Vector3(-1,-1,-1)
        self.position = Vector3(-1,-1,-1)
        self.capture_points = 0
        self.shoot_range_bonus = 0

# Abstract class for action made by player
# Just holds data about action
class GameAction(): 
    def __init__(self, player_id, action_type):
        self.player_id = player_id
        self.action_type = action_type
    
    # Returns action data as json
    def get_data(self):
        raise NotImplementedError("Child class must override this method")

class GameActionType(IntEnum):
    CHAT = 100,
    MOVE = 101,
    SHOOT = 102

class ChatAction(GameAction):
    def __init__(self, player_id, message):
        super(ChatAction, self).__init__(player_id, GameActionType.CHAT)
        self.message = message
    def get_data(self):
        return self.message


class MoveAction(GameAction):
    def __init__(self, player_id, vehicle_id, target):
        super(MoveAction, self).__init__(player_id, GameActionType.MOVE)
        self.vehicle_id = vehicle_id
        self.target = target # location
    def get_data(self):
        return {"vehicle_id" : self.vehicle_id, "target" : self.target}


class ShootAction(GameAction):
    def __init__(self, player_id, vehicle_id, target):
        super(ShootAction, self).__init__(player_id, GameActionType.SHOOT)
        self.vehicle_id = vehicle_id
        self.target = target
    def get_data(self):
        return {"vehicle_id" : self.vehicle_id, "target" : self.target}
