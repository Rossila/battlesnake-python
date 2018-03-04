import bottle
import json
import os
import random
from enum import Enum

class State:
    survival = 1
    food_list = []
    food_snake_list = []
    # list of positions of snake heads (not including yourself)
    snake_list = []
    your_snake_point = None
    your_snake_length = 0
    your_snake_health = 0
    board = None
    board_width = 0
    board_height = 0

    def __init__(self):
        pass

def newPoint(x, y):
   return Point({'x': x, 'y':y})

class Snake:
    point = None
    length = 0
    def __init__(self, point, length):
        self.point = point
        self.length = length

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
    old_moves = filtered_moves
    filtered_moves = avoid_traps(state, directions)
    if (not filtered_moves or len(filtered_moves) < 1):
        filtered_moves = old_moves
    direction = choose_move(data, filtered_moves, state)
    printStuff(direction)
    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }


def choose_move(data, directions, state):
    target = target_food_point(state)
    your_snake_point = state.your_snake_point

    printStuff('available directions')
    printStuff(directions)
    direction = random.choice(directions)

    if target.x > your_snake_point.x and 'right' in directions:
        direction = 'right'
    elif (target.x < your_snake_point.x) and 'left' in directions:
        direction = 'left'
    elif (target.y > your_snake_point.y) and 'down' in directions:
        direction = 'down'
    elif (target.y < your_snake_point.y) and 'up' in directions:
        direction = 'up'


    return direction

def avoid_traps(state, directions):
    if state.survival == 1:
        your_snake_point = state.your_snake_point
        area_up = 0
        area_down = 0
        area_left = 0
        area_right = 0
        for direction in directions:
            # up
            if (direction == 'up'):
                area_up = len(bfs(state, newPoint(your_snake_point.x, your_snake_point.y - 1)))
                print 'up'
                print area_up
                if area_up < state.your_snake_length:
                    directions.remove('up')
            elif (direction == 'down'):
                area_down = len(bfs(state, newPoint(your_snake_point.x, your_snake_point.y + 1)))
                print 'down'
                print area_down
                if area_down < state.your_snake_length:
                    directions.remove('down')
            elif (direction == 'left'):
                area_left = len(bfs(state, newPoint(your_snake_point.x - 1, your_snake_point.y)))
                print 'left'
                print area_left
                if area_left < state.your_snake_length:
                    directions.remove('left')
            elif (direction == 'right'):
                # right
                area_right = len(bfs(state, newPoint(your_snake_point.x + 1, your_snake_point.y)))
                print 'right'
                print area_right
                if area_right < state.your_snake_length:
                    directions.remove('right')

    return directions

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
    your_snake_length = len(data.get('you').get('body').get('data'))
    your_snake_health = data.get('you').get('health')

    # add snakes
    snake_list_data = data.get('snakes').get('data')
    for snake in snake_list_data:
        if snake.get('health') == 0:
            continue
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
                    length = len(snake_data)
                    snake_list.append(Snake(point, length))
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
    state.your_snake_length = your_snake_length
    state.board_width = data.get('width')
    state.board_height = data.get('height')

    target_snakes(state)

    return state

def valid_moves(data, directions, state):
    directions = no_wall(data, directions, state)
    directions = no_suicide(data, directions, state)
    return directions

def willCollide(state, poi):
    if state.your_snake_point.squaredDistance(poi) < 2:
        for snake in state.snake_list:
            if snake.point.squaredDistance(poi) < 2:
                return True
    return False

def target_food_point(state):
    closest_point = state.food_list[0]
    your_snake_point = state.your_snake_point
    squaredDistance = -1

    for food_point in state.food_list:
        if squaredDistance < 0 or your_snake_point.squaredDistance(food_point) < squaredDistance and not willCollide(state, food_point):
            squaredDistance = your_snake_point.squaredDistance(food_point)
            closest_point = food_point

    # eat other snakes in select scenarios
    if closest_point > 3 and state.your_snake_health > 15:
        squaredDistance = -1
        printStuff('FOOOOOD')
        printStuff(food_snake_list)
        for food_point in state.food_snake_list:
            if squaredDistance < 0 or your_snake_point.squaredDistance(food_point) < squaredDistance:
                squaredDistance = your_snake_point.squaredDistance(food_point)
                closest_point = food_point

    return closest_point

def no_wall(data, directions, state):
    head = state.your_snake_point
    # up
    if head.y == 0 and 'up' in directions:
        directions.remove('up')
    # down
    if head.y == len(state.board) - 1 and 'down' in directions:
        directions.remove('down')
    # left
    if head.x == 0 and 'left' in directions:
        directions.remove('left')
    # right
    if head.x == len(state.board[0]) - 1 and 'right' in directions:
        directions.remove('right')

    return directions


def no_suicide(data, directions, state):
    first = state.your_snake_point
    currBoard = state.board

    if 'up' in directions:
        next_x = first.x
        next_y = first.y - 1
        printStuff(currBoard[next_y][next_x])
        if currBoard[next_y][next_x] == NodeType.SNAKE_HEAD or currBoard[next_y][next_x] == NodeType.SNAKE_BODY:
            directions.remove('up')
    if 'down' in directions:
        next_x = first.x
        next_y = first.y + 1
        printStuff(currBoard[next_y][next_x])
        if currBoard[next_y][next_x] == NodeType.SNAKE_HEAD or currBoard[next_y][next_x] == NodeType.SNAKE_BODY:
            directions.remove('down')
    if 'left' in directions:
        next_x = first.x - 1
        next_y = first.y
        printStuff(currBoard[next_y][next_x])
        if currBoard[next_y][next_x] == NodeType.SNAKE_HEAD or currBoard[next_y][next_x] == NodeType.SNAKE_BODY:
            directions.remove('left')
    if 'right' in directions:
        next_x = first.x + 1
        next_y = first.y
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


def target_snakes(state):
    for snake in state.snake_list:
        if snake.length < state.your_snake_length:
            # this snake is edible. Travel towards a valid move of its
            otherState = State()
            otherState.food_list = state.food_list
            otherState.snake_list = state.snake_list
            otherState.your_snake_point = snake.point
            otherState.board = state.board
            otherState.your_snake_length = snake.length
            otherState.your_snake_health = state.your_snake_health

            directions = valid_moves(None, ['up', 'down', 'left', 'right'], otherState)
            direction = random.choice(directions)
            new = None
            if (direction == 'up'):
                new = newPoint(snake.point.x, snake.point.y - 1)
            elif (directions == 'down'):
                new = newPoint(snake.point.x, snake.point.y + 1)
            elif (directions == 'left'):
                new = newPoint(snake.point.x - 1, snake.point.y)
            elif (directions == 'right'):
                new = newPoint(snake.point.x + 1, snake.point.y)
            if new:
                state.food_snake_list.append(new)

def valid_square(point, state):
    return state.board[point.y][point.x] == NodeType.EMPTY or state.board[point.y][point.x] == NodeType.FOOD


def bfs(state, point):
    board_width = state.board_width
    board_height = state.board_height
    visited = [[False for width in range(board_width)] for height in range(board_height)]
    queue = []
    queue.append(point)
    visited[point.y][point.x] = True

    while queue:
        s = queue.pop(0)

        if point.x > 0:
            p = newPoint(point.x - 1, point.y)
            if valid_square(p, state) and visited[p.y][p.x] == False:
                visited[p.y][p.x] = True
                queue.append(p)
        if point.y > 0:
            p = newPoint(point.x, point.y - 1)
            if valid_square(p, state) and visited[p.y][p.x] == False:
                visited[p.y][p.x] = True
                queue.append(p)
        if point.y < len(state.board) - 1:
            p = newPoint(point.x, point.y + 1)
            if valid_square(p, state) and visited[p.y][p.x] == False:
                visited[p.y][p.x] = True
                queue.append(p)
        if point.x < len(state.board[0]) - 1:
            p = newPoint(point.x + 1, point.y)
            if valid_square(p, state) and visited[p.y][p.x] == False:
                visited[p.y][p.x] = True
                queue.append(p)

    return visited



def calc_area(point, state, visited):
    if point.x > 0 and point.x < len(state.board[0]) - 1 and point.y > 0 and point.y < len(state.board) - 1:
        # left
        p = newPoint(point.x - 1, point.y)
        if valid_square(p, state) and p not in visited:
	    visited.add(p)
	    calc_area(p, state, visited)
        # up
        p = newPoint(point.x, point.y - 1)
        if valid_square(p, state) and p not in visited:
            visited.add(p)
    	    calc_area(p, state, visited)
        # right
        p = newPoint(point.x + 1, point.y)
        if valid_square(p, state) and p not in visited:
            visited.add(p)
    	    calc_area(p, state, visited)
        # down
        p = newPoint(point.x, point.y + 1)
        if valid_square(p, state) and p not in visited:
            visited.add(p)
    	    calc_area(p, state, visited)

    return len(visited)

def printGrid(cur_snake_board):
    for y in range(len(cur_snake_board)):
        printStuff(cur_snake_board[y])

def printStuff(stuff):
    return
    print stuff

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
