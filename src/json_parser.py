from dataclasses import asdict
import json

from traitlets import Integer
import wg_game

def PlayerJsonDecoder(json_str):
    data = json.loads(json_str)
    return wg_game.Player(data['idx'], data['name'], data['is_observer'])

def Vector3JsonDecoder(json_str):
    data = json.loads(json_str)
    return wg_game.Vector3(data['x'], data['y'], data['z'])

def parse_dict_vector3(dct):
    return wg_game.Vector3(**dct)

def parse_dict_vehicle(dct):
    vehicle = wg_game.Vehicle()
    vehicle.player_id = dct['player_id']
    vehicle.vehicle_type = dct['vehicle_type']
    vehicle.health = dct['health']
    vehicle.spawn_position = parse_dict_vector3(dct['spawn_position'])
    vehicle.position = parse_dict_vector3(dct['position'])
    vehicle.capture_points = dct['capture_points']
    vehicle.shoot_range_bonus = dct['shoot_range_bonus']
    return vehicle

def GameStateJsonDecoder(json_str):
    data = json.loads(json_str)
    state = wg_game.GameState()
    state.num_players = data['num_players']
    state.num_turns = data['num_turns']
    state.num_rounds = data['num_rounds']
    state.current_turn = data['current_turn']
    state.current_round = data['current_round']
    state.current_player_idx = data['current_player_idx']
    state.finished = data['finished']
    state.winner = data['winner']
    
    state.players = []
    for player_data in data['players']:
        player = wg_game.Player(**player_data)
        state.players.append(player)
    
    state.observers = []
    for player_data in data['observers']:
        player = wg_game.Player(**player_data)
        state.observers.append(player)

    for key in data['win_points'].keys():
        state.win_points[int(key)] = (data['win_points'][key]['capture'], data['win_points'][key]['kill'])

    for key in data['player_result_points'].keys():
        state.player_result_points[int(key)] = data['player_result_points'][key]
    
    state.catapult_usage = []
    for catapult in data['catapult_usage']:
        state.catapult_usage.append(parse_dict_vector3(catapult))

    for key in data['attack_matrix'].keys():
        atk_list = []
        for idx in data['attack_matrix'][key]:
            atk_list.append(int(idx))
        state.attack_matrix[int(key)] = atk_list

    for keys in data['vehicles'].keys():
        state.vehicles[int(key)] = parse_dict_vehicle(data['vehicles'][key])
    return state


def GameMapJsonDecoder(json_str):
    data = json.loads(json_str)
    gmap = wg_game.GameMap()
    gmap.size = data['size']
    gmap.name = data['name']
    gmap.entity_map = dict()

    content = data['content']
    for key in content.keys():
        gmap.entity_map[key] = []
        for location in content[key]:
            gmap.entity_map[key].append(parse_dict_vector3(location))
    for spawn_point_dict in data['spawn_points']:
        gmap.spawn_points.append(spawn_point_dict)

    return gmap
    
def parse_dict_game_action(dct):
    action_type = dct['action_type']
    player_id = dct['player_id']

    action_enum = wg_game.GameActionType(action_type)
    match action_enum:
        case wg_game.GameActionType.CHAT:
            action = wg_game.ChatAction(player_id, dct['data']['message'])
        case wg_game.GameActionType.MOVE:
            action = wg_game.MoveAction(player_id, dct['data']['vehicle_id'], parse_dict_vector3(dct['data']['target']))
        case wg_game.GameActionType.SHOOT:
            action = wg_game.ShootAction(player_id, dct['data']['vehicle_id'], parse_dict_vector3(dct['data']['target']))

    return action

def GameTurnsJsonDecoder(json_str):
    data = json.loads(json_str)
    turns = []
    for turn in data['actions']:
        turns.append(parse_dict_game_action(turn))
    return turns

def ActionEncodeJson(action):
    data = dict()
    if action.action_type == wg_game.GameActionType.CHAT:
        data['message'] = action.get_data()
    else:
        data['vehicle_id'] = action.get_data()['vehicle_id']
        position = dict(asdict(action.get_data()['target']))
        data['target'] = position
        
    return json.dumps(data)

