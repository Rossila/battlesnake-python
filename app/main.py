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
    currBoard = current_board(data)

    filtered_moves = valid_moves(data, directions, currBoard)
    direction = choose_move(data, filtered_moves, currBoard)
    print direction
    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }


def choose_move(data, direction, currBoard):
    return random.choice(direction)

def current_board(data):
    board_width = data.get('width')
    board_height = data.get('height')

    cur_snake_board = [[nodeType.EMPTY for width in range(board_width)] for height in range(board_height)]

    # add food
    food_list = data.get('food').get('data')
    for food in food_list:
        cur_snake_board[food.get('x')][food.get('y')] = nodeType.FOOD

    # add snakes
    snake_list = data.get('snakes').get('data')
    for snake in snake_list:
        for index, point in enumerate(snake.get('body').get('data')):
            if index == 0:
                # snake head
                type = nodeType.SNAKE_HEAD
            else:
                ctype = nodeType.SNAKE_BODY
            cur_snake_board[point.get('x')][point.get('y')] = type

    return cur_snake_board


def valid_moves(data, directions, currBoard):
    directions = no_wall(data, directions, currBoard)
    directions = no_suicide(data, directions, currBoard)
    return directions


def no_wall(data, directions, currBoard):
    you = data.get('you')
    head = you.get('body').get('data')[0]
    # up
    if head.get('y') == 0 and 'up' in directions:
        directions.remove('up')
    # down
    if head.get('y') == data.get('height') - 1 and 'down' in directions:
        directions.remove('down')
    # left
    if head.get('x') == 0 and 'left' in directions:
        directions.remove('left')
    # right
    if head.get('x') == data.get('width') - 1 and 'right' in directions:
        directions.remove('right')

    return directions


def no_suicide(data, directions, currBoard):
    you = data.get('you')
    first = you.get('body').get('data')[0]

    if 'up' in directions:
        next_x = first.get('x')
        next_y = first.get('y') - 1
        print currBoard[next_x][next_y]
        if currBoard[next_x][next_y] == nodeType.SNAKE_HEAD or currBoard[next_x][next_y] == nodeType.SNAKE_BODY:
            directions.remove('up')
    if 'down' in directions:
        next_x = first.get('x')
        next_y = first.get('y') + 1
        print currBoard[next_x][next_y]
        if currBoard[next_x][next_y] == nodeType.SNAKE_HEAD or currBoard[next_x][next_y] == nodeType.SNAKE_BODY:
            directions.remove('down')
    if 'left' in directions:
        next_x = first.get('x') - 1
        next_y = first.get('y')
        print currBoard[next_x][next_y]
        if currBoard[next_x][next_y] == nodeType.SNAKE_HEAD or currBoard[next_x][next_y] == nodeType.SNAKE_BODY:
            directions.remove('left')
    if 'right' in directions:
        next_x = first.get('x') + 1
        next_y = first.get('y')
        print currBoard[next_x][next_y]
        if currBoard[next_x][next_y] == nodeType.SNAKE_HEAD or currBoard[next_x][next_y] == nodeType.SNAKE_BODY:
            directions.remove('right')

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
