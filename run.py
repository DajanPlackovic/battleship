# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from re import findall
from random import randint, choice

ships = {
  "carrier" : 5,
  "battleship": 4,
  "cruiser": 3,
  "submarine": 3,
  "destroyer": 2
}

directions = {
  "N": [-1, 0],
  "S": [1, 0],
  "W": [0, -1],
  "E" : [0, 1]
}

states = {
  "ship": "■",
  "orient": "□",
  "hit": "X",
  "miss": "O",
  "unmarked": "·"
}

class Board():
  """
  Initalizes a board:
  
  A dictionary with coordinate tuplets as keys, field states as values
  and methods that allow actions upon the board.
  """
  def __init__(self, user = True, state = None):
    self.state = state if state else {}
    for i in range(8):
      for j in range(8):
        self.state[(i, j)] = "unmarked"
    
    self.last_move = None
    self.opponent = not user
  
  def update_point(self, coordinates, new_state):
    """
    Updates the state of a point and saves that state as the last move.
    """
    self.state[coordinates] = new_state
    self.last_move = (coordinates, new_state)

  def display_board(self):
    """
    Prints current state of the board with columns and rows indicated.
    """
    board_display = [ list(['·'] * 8) for i in range(8) ]
    for point in self.state:
      if self.opponent and self.state[point] == "ship":
        continue
      row, column = point
      board_display[row][column] = states[self.state[point]]

    for idx in range(len(board_display)):
      print('  '.join([str(idx + 1), ' '.join(board_display[idx])]))
    print('   ' + ' '.join([ str(letter) for letter in columns ]))

  

boards = {
  "user" : Board(),
  "computer": Board()
}

columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
rows = [str(num) for num in range(1,9)]

def display_rules():
  """
  Show all the rules at the beginning of the game.
  """
  input("""
Welcome to BATTLESHIP!
        
Whenever you see the symbol at the bottom of this message, press any key to continue.
        
⏎
""")
  
  input_test = input("""
Whenever you instead see the symbol below, you will be asked to input something.
        
Type anything in and press Enter. Just don't leave it blank. ⇒
""")
  
  while len(input_test) == 0:
    input_test = input("""
See, that's the one thing that won't work. When you see the ⇒ arrow, you gotta type something.
                       
Try again ⇒
""")
  

# place_ships and its subfunctions

def parse_input(input):
  """
  Parses the input of a square for placing ships or targeting enemy ships.
  If the input is not valid, returns a ValueError.
  """
  processed_input = input.strip().replace(" ","")
  try:
    if (len(processed_input) > 2):
        raise ValueError(f"Input can contain only two characters (a letter A-H and a number 1-8) and spaces.\nInput contains {len(processed_input)} characters.")
    
    column = findall(f"[{''.join(columns)}]", input.upper())
    
    if len(column) < 1:
      raise ValueError(f"Input string should contain exactly one reference\nto column (a letter from A to H or a to h).\n")
    
    row = findall(f"[{''.join(rows)}]", input)
    if len(row) < 1:
      raise ValueError(f"Input string should contain exactly one reference\nto row (a number from 1 to 8).\n")
    
    return [ int(row[0]) - 1, columns.index(column[0]) ]
  
  except Exception as e:
    raise ValueError(f"Input not accepted: {e}\n\n⏎\n")

def find_legitimate_directions(board, starting_square, ship_length):
  """
  Returns legitimate orientations for placing the ships, that do not go
  out of bounds or intersect an already placed ship.
  """
  legitimate_directions = []
  row, column = starting_square

  for direction in directions:
    row_mod = directions[direction][0]
    col_mod = directions[direction][1]

    counter = 0
                        
    for idx in range(ship_length):
      new_row = row + idx * row_mod
      if not(0 <= new_row <= 7):
        continue

      new_col = column + idx * col_mod
      if not(0 <= new_col <= 7):
        continue

      if board.state[(row, column)] != "unmarked":
        continue
      
      counter += 1
    
    if counter == ship_length:
        legitimate_directions.append(direction)
        

  if len(legitimate_directions) == 0:
    raise ValueError("Ship cannot be placed in any orientation from the chosen starting position\nwithout overlapping another ship or going out of bounds.\n\n⏎")
  
  return legitimate_directions

def showDirections(board, starting_square, legitimate_directions, ship_length):
  """
  Displays the available orientations when placing ships.
  """
  row, column = starting_square

  board_orientation = Board(board.state)
  board_orientation.state[(row, column)] = "ship"

  for direction in legitimate_directions:
    for idx in range(1, ship_length):
      board_orientation.state[(row + idx * directions[direction][0], column + idx * directions[direction][1])] = "orient"

  board_orientation.display_board()


def implement_direction(board, starting_square, direction, legitimate_directions, ship_length):
  """
  Accept direction input if legitimate, throw error if not legitimate.
  """
  direction = direction.upper()
  if not(direction in legitimate_directions):
    raise ValueError(f"{direction} is not one of the possible directions.")
  
  row, column = starting_square
  
  for idx in range(ship_length):
    board.state[(row + idx * directions[direction][0], column + idx * directions[direction][1])] = "ship"
  

def place_ships(user, test=False):
  """
  When user is set to True, loops through the available ships and
  lets the user set them up on their board.

  When user is set to False, automatically generates the board
  setup for the computer.
  """
  if user and not test:
    input(
"""
Start by placing your ships. You can do so by first entering a point
on the board (e.g. A2) and then choosing an orientation (N, E, S, W).

⏎
""")
  for ship in ships:
    got_input = False
    while not(got_input):
      if user and not test:
        boards["user"].display_board()
      starting_square = input(f"Place the {ship.capitalize()}: Length {ships[ship]} ⇒\n") if user and not test else [ randint(0, 7), randint(0, 7) ]
      try:
        if user and not test:
          starting_square = parse_input(starting_square)
        legitimate_directions = find_legitimate_directions(boards["user"] if user else boards["computer"], starting_square, ships[ship])
      except Exception as e:
        if user and not test:
          input(e)
        continue

      got_orientation = False
      while not(got_orientation):
        try:
          if user and not test:
            showDirections(boards["user"] if user else boards["computer"], starting_square, legitimate_directions, ships[ship])
          chosen_direction = input(f"Choose the orientation of the ship: [N]orth, [E]ast, [S]outh or [W]est.\nBased on the starting position, the following orientations are possible:\n{', '.join(legitimate_directions)} ⇒\n") if user and not test else choice(legitimate_directions)
          implement_direction(boards["user"] if user else boards["computer"], starting_square, chosen_direction, legitimate_directions, ships[ship])
          got_orientation = True
        except Exception as e:
          if user and not test:
            print(e)
          continue

      got_input = True 


# game_loop and subfunctions
def check_hit(target, target_board, user):
  """
  Check if the target was hit, update the board accordingly.
  
  Raise error if user retargets same spot.
  """
  row, column = target

  target_match = [ index for index, point in enumerate(target_board) if point[0] == row and point[1] == column ]

  new_state = "miss"

  if len(target_match):
    if target_board[target_match[0]][2] == "ship":
      if not user:
        input(f"Let's see... I think I'll go for {columns[column] + rows[row]}.")
      new_state = "hit"
      target_board[target_match[0]][2] = new_state
      message = """
Nice! You got one!
 ⏎
""" if user else """
Nice! I got you!
⏎
"""
    else:
      raise ValueError("You already targeted that spot! Pick another one.\n\n⏎")
  else:
    target_board.append([row, column, new_state])
    if not user:
      input(f"Let's see... I think I'll go for {columns[column] + rows[row]}.")
    message = """
Yikes! Better luck next time...
 ⏎
""" if user else """
Damn! I'm sure I was close.
⏎
"""

  return message


def game_loop():
  def computer_choose_target():
    return [ randint(0,7), randint(0,7) ]
        

  def turn(user):
    global prior_outcome
    target_board = boards["computer"] if user else boards["user"]
    got_input = False
    while not got_input:
      print_board(target_board, user)
      target = input("""
Enter a field you would like to target. ⇒
""") if user else computer_choose_target()
      try:
        if user:
          target = parse_input(target)
        message = check_hit(target, target_board, user)
        got_input = True
      except Exception as e:
        if user:
          input(e)
    print_board(target_board, user)
    input(message)
  
  while sum(point[2] == 'ship' for point in boards['computer']) > 0 and sum(point[2] == 'ship' for point in boards['user']) > 0:
    # turn(user=True)
    turn(user=False)

def main():
  """
  Runs all of the programme functionality.
  """
  # display_rules()
  # place_ships(user=True, test=True)
  # place_ships(user=False)
  # game_loop()
  place_ships(user=True)
  boards["user"].update_point((0,0), "ship")
  boards["user"].display_board()
  showDirections(boards["user"], (0,0), ["S", "E"], 5)

main()