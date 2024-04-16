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
    self.ship_count = sum(ships.values())
  
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
  
  def find_legitimate_directions(self, starting_square, ship):
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

      for idx in range(ships[ship]):
        new_row = row + idx * row_mod
        if not(0 <= new_row <= 7):
          continue

        new_col = column + idx * col_mod
        if not(0 <= new_col <= 7):
          continue

        if self.state[(row, column)] != "unmarked":
          continue
      
        counter += 1
    
      if counter == ships[ship]:
        legitimate_directions.append(direction)
        

    if len(legitimate_directions) == 0:
      raise ValueError("Ship cannot be placed in any orientation from the chosen starting position\nwithout overlapping another ship or going out of bounds.\n\n⏎")
  
    return legitimate_directions

  def show_directions(self, starting_square, legitimate_directions, ship):
    """
    Displays the available orientations when placing ships.
    """
    row, column = starting_square

    self.state[(row, column)] = "ship"

    for direction in legitimate_directions:
      for idx in range(1, ships[ship]):
        self.state[(row + idx * directions[direction][0], column + idx * directions[direction][1])] = "orient"

    self.display_board()

  def implement_direction(self, starting_square, direction, legitimate_directions, ship):
    """
    Accept direction input if legitimate, throw error if not legitimate.
    """
    direction = direction.upper()
    if not(direction in legitimate_directions):
      raise ValueError(f"{direction} is not one of the possible directions.")
    
    row, column = starting_square
    
    self.state = { point: "unmarked" if state == "orient" else state for point, state in self.state.items() }
    
    for idx in range(ships[ship]):
      self.state[(row + idx * directions[direction][0], column + idx * directions[direction][1])] = "ship"

  def check_hit(self, target):
    """
    Check if the target was hit, update the board accordingly.
    
    Raise error if user retargets same spot.
    """
    row, column = target

    retarget_error = ValueError("You already targeted that spot! Pick another one.\n\n⏎")

    match self.state[(row, column)]:
      case "hit":
        raise retarget_error
      case "miss":
        raise retarget_error
      case "ship":
        if not self.opponent:
          input(f"Let's see... I think I'll go for {columns[column] + rows[row]}.")
        self.state[(row, column)] = "hit"

        message = """
  Nice! You got one!
  ⏎
  """ if self.opponent else """
  Nice! I got you!
  ⏎
  """
      case "unmarked":
        if not self.opponent:
          input(f"Let's see... I think I'll go for {columns[column] + rows[row]}.")
        self.state[(row, column)] = "miss"

        message = """
    Yikes! Better luck next time...
    ⏎
    """ if self.opponent else """
    Damn! I'm sure I was close.
    ⏎
    """

    return message
  

boards = {
  "user" : Board(),
  "computer": Board(user=False)
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

def place_ships(user, test=False):
  board = boards["user"] if user else boards["computer"]
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
        board.display_board()
      starting_square = input(f"Place the {ship.capitalize()}: Length {ships[ship]} ⇒\n") if user and not test else [ randint(0, 7), randint(0, 7) ]
      try:
        if user and not test:
          starting_square = parse_input(starting_square)
        legitimate_directions = board.find_legitimate_directions(starting_square, ship)
      except Exception as e:
        if user and not test:
          input(e)
        continue

      got_orientation = False
      while not(got_orientation):
        try:
          if user and not test:
            board.show_directions(starting_square, legitimate_directions, ship)
          chosen_direction = input(f"Choose the orientation of the ship: [N]orth, [E]ast, [S]outh or [W]est.\nBased on the starting position, the following orientations are possible:\n{', '.join(legitimate_directions)} ⇒\n") if user and not test else choice(legitimate_directions)
          board.implement_direction(starting_square, chosen_direction, legitimate_directions, ship)
          got_orientation = True
        except Exception as e:
          if user and not test:
            print(e)
          continue

      got_input = True 


# game_loop and subfunctions


def game_loop():
  def computer_choose_target():
    # already_hit = [point for point in boards["user"] if point[2] == "hit"]
    
    # if len(already_hit) == 0:
      return [ randint(0,7), randint(0,7) ]
    
    # last_hit = already_hit[-1]
        

  def turn(user):
    global prior_outcome
    target_board = boards["computer"] if user else boards["user"]
    got_input = False
    while not got_input:
      target_board.display_board()
      target = input("""
Enter a field you would like to target. ⇒
""") if user else computer_choose_target()
      try:
        if user:
          target = parse_input(target)
        message = target_board.check_hit(target)
        got_input = True
      except Exception as e:
        if user:
          input(e)
    target_board.display_board()
  
    input(message)
  
  while boards["computer"].ship_count > 0 and boards["user"].ship_count > 0:
    turn(user=True)
    turn(user=False)

def main():
  """
  Runs all of the programme functionality.
  """
  # display_rules()
  place_ships(user=True, test=True)
  place_ships(user=False)
  # print(boards["computer"].ship_count)
  game_loop()

main()