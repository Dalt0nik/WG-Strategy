from dataclasses import dataclass

@dataclass
class Location:
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
        players = []
        
        # Our player, we can keep more data about them
        client = None

        self.observers = []
        self.current_player_idx = 0
        self.finished = False
        vehicles = []
        attack_matrix = None
        winner = 0
        win_points = None
        player_result_points = None
        catapult_usage = None


# game map
# for more info look at documentation, Map Response
# all data about game entity locations
class GameMap:
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.spawn_points = None
        content = None

# Player (client)
# init only client, game state keeps track of other players
# can make GameActions
class Player:
    def __init__(self, name):
        self.name = name
        self.id = -1
    
    def make_action(action):
        # tell game to make action, game tells networking subsystem to pass action
        ...

# able to pass data to player
class ControllerInterface:
    def __init__(self):
        pass

# Reads Console Input, should pass data to player
# ONLY OPTIONAL, We don't need to do it now
class ConsoleController(ControllerInterface):
    def __init__(self):
        pass

    def get_input(self):
        pass

# Uses AI Behavior Algorithms to pass data to player
class AIController(ControllerInterface):
    def __init__(self):
        pass

    def make_decision(self):
        pass

# Hexagon entities
class GameEntity:
    def __init__(self, location):
        self.location = location # x,y,z
        # add more here?

# Base class for all vehicles OR all vehicles if there is no need to make more classes
class Vehicle(GameEntity):
    def __init__(self):
        ...
        pass

# Abstract class for action made by player
# Just holds data about action made
class GameAction(): 
    def __init__(self, player, action_type):
        self.player = player
        self.action_type = action_type
    
    # Returns action data as json
    def get_json():
        ...

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


