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
import json
import json_parser
import heapq
import connection
from urllib.parse import urlparse



# Creates a move request
# def create_move_request(vehicle_move):
#     encoded_message = vehicle_move.encode('utf-8')
#     bytes_length = len(encoded_message)
#     message_len_in_byte_format = struct.pack('<i', bytes_length)

#     # Concatenate the bytes objects and the JSON bytes
#     # b'\x65\x00\x00\x00' + b'\x2E\x00\x00\x00 + {"vehicle_id":5,"target":{"x":-1,"y":1,"z":0}}
#     # = b'\x65\x00\x00\x00\x2E\x00\x00\x00{"vehicle_id":5,"target":{"x":-1,"y":1,"z":0}}'
#     combined_move = move_request + message_len_in_byte_format + encoded_message
#     return combined_move

# login_request = b'\x01\x00\x00\x00\x10\x00\x00\x00{"name": "Lion"}'
# logout_request = b'\x02\x00\x00\x00\x00\x00\x00\x00'
# map_request = b'\x03\x00\x00\x00\x00\x00\x00\x00'
# game_state_request = b'\x04\x00\x00\x00\x00\x00\x00\x00'
# game_actions_request = b'\x05\x00\x00\x00\x00\x00\x00\x00'
# turn_request = b'\x06\x00\x00\x00\x00\x00\x00\x00'

# move_request = b'\x65\x00\x00\x00'


# def data_to_json(data):
#     json_string = data.decode('utf-8', 'ignore')
#     start_index = json_string.find('{')
#     json_data_str = json_string[start_index:]
#     return json_data_str


# server = connection.ServerConnection('http://wgforge-srv.wargaming.net', 443)
# server.connect()

# data = server.send_request(login_request)
# json_data_str = data_to_json(data)
# response = json_parser.LoginJsonDecoder(json_data_str)
# print(response.player_id)


# #Game Map Data
# data = server.send_request(map_request)
# json_data_str = data_to_json(data)
# game_map = json_parser.GameMapJsonDecoder(json_data_str)

# #Game State Data
# data = server.send_request(game_state_request)
# json_data_str = data_to_json(data)
# game_state = json_parser.GameStateJsonDecoder(json_data_str)


# position_tuple = (game_state.vehicles[1].position.x, game_state.vehicles[1].position.y)
# print(position_tuple)
# base_tuple = (game_map.get_all_base()[0].x, game_map.get_all_base()[0].y)

# position_to_go = find_path(position_tuple, base_tuple, game_state)[1]

# # Coordinates
# x = position_to_go[0]
# y = position_to_go[1]
# z = -(x+y)

# move_json = {
#     "vehicle_id": 1,
#     "target": {
#         "x": x,
#         "y": y,
#         "z": z
#     }
# }
# # Convert dictionary to JSON string
# json_string = json.dumps(move_json)
# vehicle_move = json_string

# combined_move_request = create_move_request(vehicle_move)

# #Send move request
# data = server.send_request(combined_move_request)


# #Making next turn
# data = server.send_request(turn_request)

# #Game State Data
# data = server.send_request(game_state_request)
# json_data_str = data_to_json(data)
# game_state = json_parser.GameStateJsonDecoder(json_data_str)

# # Positions of vehicles
# for vehicle_index in game_state.vehicles:

#     print(game_state.vehicles[vehicle_index].position)



# # Logout
# data = server.send_request(logout_request)
# print("Logged out")

# server.close()

game = wg_game.Game("Tank")

# game.game_loop()
    




