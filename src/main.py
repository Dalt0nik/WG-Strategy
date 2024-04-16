'''
    For now it goes like this:
        1. Login
        2. Loop:
            a. GetMap
            a. Get GameState
            b. Make turn with each vehicle //In progress//
'''
import struct
import wg_game
import socket
import json
import json_parser
import heapq
import connection
from urllib.parse import urlparse

# Distance between two hexes
def hex_distance(a, b):
    return (abs(a[0] - b[0]) + abs(a[0] + a[1] - b[0] - b[1]) + abs(a[1] - b[1])) // 2

# 0.1v pathfinding. One goal, no check for vehicles as obstacles. Star and goal are tuples.
# Given goal, returns the shortest path
def find_path(start, goal, max_iterations=100):
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
            occupied = False
            if occupied:
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
    
# def get_server_ip(http_link):
#     # Parse the URL to extract the hostname
#     parsed_url = urlparse(http_link)
#     hostname = parsed_url.hostname
    
#     # Resolve the hostname to an IP address
#     ip_address = socket.gethostbyname(hostname)
    
#     return ip_address

# Creates a move request
def create_move_request(vehicle_move):
    encoded_message = vehicle_move.encode('utf-8')
    bytes_length = len(encoded_message)
    message_len_in_byte_format = struct.pack('<i', bytes_length)

    # Concatenate the bytes objects and the JSON bytes
    # b'\x65\x00\x00\x00' + b'\x2E\x00\x00\x00 + {"vehicle_id":5,"target":{"x":-1,"y":1,"z":0}}
    # = b'\x65\x00\x00\x00\x2E\x00\x00\x00{"vehicle_id":5,"target":{"x":-1,"y":1,"z":0}}'
    combined_move = move_request + message_len_in_byte_format + encoded_message
    return combined_move

login_request = b'\x01\x00\x00\x00\x10\x00\x00\x00{"name": "Maus"}'
logout_request = b'\x02\x00\x00\x00\x00\x00\x00\x00'
map_request = b'\x03\x00\x00\x00\x00\x00\x00\x00'
game_state_request = b'\x04\x00\x00\x00\x00\x00\x00\x00'
game_actions_request = b'\x05\x00\x00\x00\x00\x00\x00\x00'
turn_request = b'\x06\x00\x00\x00\x00\x00\x00\x00'

move_request = b'\x65\x00\x00\x00'


def data_to_json(data):
    json_string = data.decode('utf-8', 'ignore')
    start_index = json_string.find('{')
    json_data_str = json_string[start_index:]
    return json_data_str


server = connection.ServerConnection('http://wgforge-srv.wargaming.net', 443)
server.connect()

data = server.send_request(login_request)

#Game Map Data
data = server.send_request(map_request)
json_data_str = data_to_json(data)
game_map = json_parser.GameMapJsonDecoder(json_data_str)

#Game State Data
data = server.send_request(game_state_request)
json_data_str = data_to_json(data)
game_state = json_parser.GameStateJsonDecoder(json_data_str)


position_tuple = (game_state.vehicles[1].position.x, game_state.vehicles[1].position.y)
print(position_tuple)
base_tuple = (game_map.get_all_base()[0].x, game_map.get_all_base()[0].y)

position_to_go = find_path(position_tuple, base_tuple)[1]

# Coordinates
x = position_to_go[0]
y = position_to_go[1]
z = -(x+y)

move_json = {
    "vehicle_id": 1,
    "target": {
        "x": x,
        "y": y,
        "z": z
    }
}
# Convert dictionary to JSON string
json_string = json.dumps(move_json)
vehicle_move = json_string

combined_move_request = create_move_request(vehicle_move)

#Send move request
data = server.send_request(combined_move_request)


#Making next turn
data = server.send_request(turn_request)

#Game State Data
data = server.send_request(game_state_request)
json_data_str = data_to_json(data)
game_state = json_parser.GameStateJsonDecoder(json_data_str)

# Positions of vehicles
for vehicle_index in game_state.vehicles:
    print(game_state.vehicles[vehicle_index].position)

    




