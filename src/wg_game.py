from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Vector3:
    x: int
    y: int
    z: int

# example
# location = Location(x, y, z)

# instance of game being played
class Game:
    def __init__(self, name):
        self.name = name
        self.state = GameState()
        self.map = GameMap()
        self.controller = AIController()

    def start(self):
        pass

    def stop(self):
        pass

# game state
# for more info look at documentation, GameState Response
# all data about current game
class GameState:
    def __init__(self):
        self.num_players = 0
        self.num_turns = 0;
        self.num_rounds = 0
        self.current_turn = 0
        self.current_round = 0
        self.players = []

        self.observers = []
        self.current_player_idx = 0
        self.finished = False
        self.vehicles = dict()
        self.attack_matrix = dict()
        self.winner = None
        self.win_points = dict() # Key is player ind, value is tuple (capture, kill points)
        self.player_result_points = dict()
        self.catapult_usage = []
        


# game map
# for more info look at documentation, Map Response
# all data about game entity locations
class GameMap:
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.spawn_points = None
        self.entity_map = dict()
        # ALL entities should go in entity_map
        # entity_map["base"] returns list of base entities
    
    def get_all_base(self):
        return self.entity_map["base"]
    def get_all_obstacles(self):
        return self.entity_map["obstacle"]
    def get_all_vehicles(self):
        return self.entity_map["vehicle"]



# Player (client and others)
class Player:
    def __init__(self, idx, name, is_observer):
        self.name = name
        self.idx = idx
        self.is_observer = is_observer


# tells networking system what to send
class Controller:
    def __init__(self):
        ...
    
    def make_action(self, action):
        ...


# Reads Console Input
# ONLY OPTIONAL, We don't need to do it now
class ConsoleController(Controller):
    def __init__(self):
        pass

    def get_input(self):
        pass

# Uses AI Behavior Algorithms to pass data to player
class AIController(Controller):
    def __init__(self):
        super.__init__(self)

    def make_decision(self):
        pass

# Hexagon entities
class GameEntity:
    def __init__(self, position):
        self.position = position # x,y,z
        # add more here?

# Base class for all vehicles OR all vehicles if there is no need to make more classes
class Vehicle(GameEntity):
    def __init__(self):
        self.player_id = 0
        self.vehicle_type = None # enum
        self.health = 1
        self.spawn_position = Vector3(-1,-1,-1)
        super(Vehicle, self).__init__(Vector3(-1,-1,-1))
        self.capture_points = 0
        self.shoot_range_bonus = 0

class Base(GameEntity):
    def __init__(self, position):
        super().__init__(position)
        ...
class Obstacle(GameEntity):
    def __init__(self, position):
        super().__init__(position)

# Abstract class for action made by player
# Just holds data about action
class GameAction(): 
    def __init__(self, player, action_type):
        self.player = player
        self.action_type = action_type
    
    # Returns action data as json
    def get_json():
        raise NotImplementedError("Child class must override this method")

class ChatAction(GameAction):
    def __init__(self, player, message):
        super().__init__(player, action_type=None) #todo
        self.message = message


class MoveAction(GameAction):
    def __init__(self, player, data):
        super().__init__(player, action_type=None) #todo
        #self.direction = direction


class ShootAction(GameAction):
    def __init__(self, player, data):
        super().__init__(player, action_type=None) #todo
        #self.target = target

