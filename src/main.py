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

game = wg_game.Game("Tank")
game.game_loop()
    




