import bottle
import json
import os
import random
from enum import Enum

class nodeType(Enum):
    EMPTY = 1
    SNAKE_HEAD = 2
    SNAKE_BODY = 3
    FOOD = 4

@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    # TODO: Do things with data
    print "*** /move TESTING ***"
    print data
    print "*** end /move TESTING ***"

    directions = ['up', 'down', 'left', 'right']
    filtered_moves = valid_moves(data, directions)
    direction = random.choice(filtered_moves)
    print direction
    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }

def currentBoard(data):
    board_width = data.get('width')
    board_height = data.get('height')

    cur_snake_board = [[nodeType.EMPTY for width in range(board_width)] for height in range(board_height)]

    food_list = data.get('food').get('data')
    for food in food_list:
        cur_snake_board[food.get('x')][food.get('y')] = nodeType.FOOD

    return cur_snake_board

def valid_moves(data, directions):
    directions = no_wall(data, directions)
    directions = no_suicide(data, directions)
    print directions
    return directions


def no_wall(data, directions):
    you = data.get('you')
    head = you.get('body').get('data')[0]
    # up
    if head.get('y') == 0 and 'up' in directions:
        directions.remove('up')
    # down
    if head.get('y') == data.get('height') - 1 and 'down' in directions:
        directions.remove('down')
    # left
    if head.get('x') == 0 and 'left' in direcitons:
        directions.remove('left')
    # right
    if head.get('x') == data.get('width') - 1 and 'right' in directions:
        directions.remove('right')

    print 'nowall dir'
    print directions
    return directions


def no_suicide(data, directions):
    you = data.get('you')
    first = you.get('body').get('data')[0]
    second = you.get('body').get('data')[1]
    last_dir = direction(second, first)

    if last_dir == 'left' and 'right' in directions:
        directions.remove('right')
    if last_dir == 'right' and 'left' in directions:
        directions.remove('left')
    if last_dir == 'up' and 'down' in directions:
        directions.remove('down')
    if last_dir == 'down' and 'up' in directions:
        directions.remove('up')

    print 'nosuicide dir'
    print directions
    return directions


def direction(a, b):
    # b is last, a is second last
    y = b.get('y') - a.get('y')
    x = b.get('x') - a.get('x')

    if y > 0:
       return 'down'
    if y < 0:
       return 'up'
    if x > 0:
       return 'right'
    if x < 0:
       return 'left'


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
