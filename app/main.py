import bottle
import json
import os
import random
from enum import Enum

class State:
    food_list = []
    # list of positions of snake heads (not including yourself)
    snake_list = []
    your_snake_point = None
    board = None

    def __init__(self):
        pass

def newPoint(x, y):
   return Point({'x': x, 'y':y})

class Point:
    x = 0
    y = 0
    def __init__(self, data):
        self.x = data.get('x')
        self.y = data.get('y')
#
    def __repr__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'
#
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        else:
            return False
#
    def __ne__(self, other):
        return not self.__eq__(other)
#
    def __hash__(self):
        return hash((self.x, self.y))
#
    def squaredDistance(self, other):
        return pow(self.x - other.x, 2) + pow(self.y - other.y, 2)

class NodeType(Enum):
    EMPTY = 1
    SNAKE_HEAD = 2
    SNAKE_BODY = 3
    FOOD = 4

    def __repr__(self):
        if (self == self.SNAKE_BODY):
            return 'B'
        elif (self == self.SNAKE_HEAD):
            return 'H'
        elif (self == self.FOOD):
            return 'F'
        else:
            return ' '

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
        'color': '#000000',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    # TODO: Do things with data
    printStuff("*** /move TESTING ***")
    printStuff(data)
    printStuff("*** end /move TESTING ***")

    directions = ['up', 'down', 'left', 'right']
    state = current_board(data)

    printGrid(state.board)

    filtered_moves = valid_moves(data, directions, state)
    direction = choose_move(data, filtered_moves, state)
    printStuff(direction)
    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }


def choose_move(data, directions, state):
    target = target_food_point(state)
    your_snake_point = state.your_snake_point

    direction = random.choice(directions)

    if target.x > your_snake_point.x and 'right' in directions:
        direction = 'right'
    elif (target.x < your_snake_point.x) and 'left' in directions:
        direction = 'left'
    elif (target.y > your_snake_point.y) and 'down' in directions:
        direction = 'down'
    elif (target.y < your_snake_point.y) and 'up' in directions:
        direction = 'up'

    # up
    area_up = calc_area(newPoint(your_snake_point.x, your_snake_point.y - 1), state, set([]), 0)
    # down
    area_down = calc_area(newPoint(your_snake_point.x, your_snake_point.y + 1), state, set([]), 0)
    # left
    area_left = calc_area(newPoint(your_snake_point.x - 1, your_snake_point.y), state, set([]), 0)
    # right
    area_right = calc_area(newPoint(your_snake_point.x + 1, your_snake_point.y), state, set([]), 0)

    max_area = max(area_up, area_down, area_left, area_right)
    if area_up == max_area and 'up' in directions:
         direction = 'up'
    if area_down == max_area and 'down' in directions:
         direction = 'down'
    if area_right == max_area and 'right' in directions:
         direction = 'right'
    if area_left == max_area and 'left' in directions:
         direction = 'left'

    return direction

def current_board(data):
    food_list = []
    snake_list = []
    your_snake_point = None

    board_width = data.get('width')
    board_height = data.get('height')

    cur_snake_board = [[NodeType.EMPTY for width in range(board_width)] for height in range(board_height)]

    # add food
    food_list_data = data.get('food').get('data')
    for food in food_list_data:
        point = Point(food)
        cur_snake_board[point.y][point.x] = NodeType.FOOD
        food_list.append(point);

    # get your snake
    your_snake_point = Point(data.get('you').get('body').get('data')[0])

    # add snakes
    snake_list_data = data.get('snakes').get('data')
    for snake in snake_list_data:
        snake_data = snake.get('body').get('data')
        for index, point in enumerate(snake_data):
            point = Point(point)
            if index == 0:
                # snake head
                type = NodeType.SNAKE_HEAD
                if your_snake_point != point:
                    printStuff('####')
                    printStuff(your_snake_point)
                    printStuff(point)
                    snake_list.append(point)
            else:
                type = NodeType.SNAKE_BODY
            cur_snake_board[point.y][point.x] = type

    printStuff('food_list')
    printStuff(food_list)

    printStuff('snake_list')
    printStuff(snake_list)

    printStuff('your_snake_point')
    printStuff(your_snake_point)

    state = State()
    state.food_list = food_list
    state.snake_list = snake_list
    state.your_snake_point = your_snake_point
    state.board = cur_snake_board

    return state

def valid_moves(data, directions, state):
    directions = no_wall(data, directions, state)
    directions = no_suicide(data, directions, state)
    return directions

def target_food_point(state):
    closest_point = state.food_list[0]
    your_snake_point = state.your_snake_point
    squaredDistance = -1
    for food_point in state.food_list:
        if squaredDistance < 0 or your_snake_point.squaredDistance(food_point) < squaredDistance:
            squaredDistance = your_snake_point.squaredDistance(food_point)
            closest_point = food_point
    return closest_point

def no_wall(data, directions, state):
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


def no_suicide(data, directions, state):
    you = data.get('you')
    first = you.get('body').get('data')[0]
    currBoard = state.board

    if 'up' in directions:
        next_x = first.get('x')
        next_y = first.get('y') - 1
        printStuff(currBoard[next_y][next_x])
        if currBoard[next_y][next_x] == NodeType.SNAKE_HEAD or currBoard[next_y][next_x] == NodeType.SNAKE_BODY:
            directions.remove('up')
    if 'down' in directions:
        next_x = first.get('x')
        next_y = first.get('y') + 1
        printStuff(currBoard[next_y][next_x])
        if currBoard[next_y][next_x] == NodeType.SNAKE_HEAD or currBoard[next_y][next_x] == NodeType.SNAKE_BODY:
            directions.remove('down')
    if 'left' in directions:
        next_x = first.get('x') - 1
        next_y = first.get('y')
        printStuff(currBoard[next_y][next_x])
        if currBoard[next_y][next_x] == NodeType.SNAKE_HEAD or currBoard[next_y][next_x] == NodeType.SNAKE_BODY:
            directions.remove('left')
    if 'right' in directions:
        next_x = first.get('x') + 1
        next_y = first.get('y')
        printStuff(currBoard[next_y][next_x])
        if currBoard[next_y][next_x] == NodeType.SNAKE_HEAD or currBoard[next_y][next_x] == NodeType.SNAKE_BODY:
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


def calc_area(point, state, visited, tries):
    if point.x > 0 and point.x < len(state.board[0]) and point.y > 0 and point.y < len(state.board):
        tries += 1
        if tries > 10000:
            print '10000 reached'
            return 0
        if point.x > 0 and state.board[point.x-1][point.y] == NodeType.EMPTY:
            p = newPoint(point.x - 1, point.y)
            if p not in visited:
    	        visited.add(newPoint(point.x - 1, point.y))
    	        calc_area(newPoint(point.x - 1, point.y), state, visited, tries)
        if point.y > 0 and state.board[point.x][point.y-1] == NodeType.EMPTY:
            p = newPoint(point.x, point.y - 1)
            if p not in visited:
                visited.add(newPoint(point.x, point.y - 1))
                calc_area(newPoint(point.x, point.y - 1), state, visited, tries)
        if point.x < len(state.board[0]) - 1 and state.board[point.x + 1][point.y] == NodeType.EMPTY:
            p = newPoint(point.x + 1, point.y)
            if p not in visited:
                visited.add(newPoint(point.x + 1, point.y))
                calc_area(newPoint(point.x + 1, point.y), state, visited, tries)
        if point.y < len(state.board) - 1 and state.board[point.x][point.y+1] == NodeType.EMPTY:
            p = newPoint(point.x, point.y + 1)
            if p not in visited:
                visited.add(newPoint(point.x, point.y + 1))
                calc_area(newPoint(point.x, point.y + 1), state, visited, tries)
    
    return len(visited)

def printGrid(cur_snake_board):
    for y in range(len(cur_snake_board)):
        printStuff(cur_snake_board[y])

def printStuff(stuff):
    return;
    print stuff

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
