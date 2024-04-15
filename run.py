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
  "miss": "O"
}

boards = {
  "user" : [],
  "computer": []
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

def print_board(board, opponent=False):
  """
  Prints current state of the board with columns and rows indicated.
  """
  board_display = [ list(['·'] * 8) for i in range(8) ]
  for point in board:
    row, column, state = point
    if opponent and state == "ship":
      continue
    board_display[row][column] = states[state]

  for idx in range(len(board_display)):
    print('  '.join([str(idx + 1), ' '.join(board_display[idx])]))
  print('   ' + ' '.join([ str(letter) for letter in columns ]))

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

      if True in (point[0] == new_row and point[1] == new_col for point in board):
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

  board_orientation = board[:]
  board_orientation.append([row, column, "ship"])

  for direction in legitimate_directions:
    for idx in range(1, ship_length):
      board_orientation.append([row + idx * directions[direction][0], column + idx * directions[direction][1], "orient"])

  return board_orientation

def implement_direction(board, starting_square, direction, legitimate_directions, ship_length):
  """
  Accept direction input if legitimate, throw error if not legitimate.
  """
  direction = direction.upper()
  if not(direction in legitimate_directions):
    raise ValueError(f"{direction} is not one of the possible directions.")
  
  row, column = starting_square
  
  for idx in range(ship_length):
    board.append([row + idx * directions[direction][0], column + idx * directions[direction][1], "ship"])
  

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
        print_board(boards["user"])
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
            print_board(showDirections(boards["user"] if user else boards["computer"], starting_square, legitimate_directions, ships[ship]))
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

  if len(target_match):
    if target_board[target_match[0]][2] == "ship":
      if not user:
        input(f"Let's see... I think I'll go for {columns[column] + rows[row]}.")
      target_board[target_match[0]][2] = "hit"
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
    target_board.append([row, column, "miss"])
    message = """
Yikes! Better luck next time...
 ⏎
""" if user else """
Damn! I'm sure I was close.
⏎
"""

  return message

def turn(user):
    target_board = boards["computer"] if user else boards["user"]
    got_input = False
    while not got_input:
      print_board(target_board, user)
      target = input("""
Enter a field you would like to target. ⇒
""") if user else [randint(0, 7), randint(0, 7)]
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
  
def game_loop():
  while sum(point[2] == 'ship' for point in boards['computer']) > 0 and sum(point[2] == 'ship' for point in boards['user']) > 0:
    turn(user=True)
    turn(user=False)

def main():
  """
  Runs all of the programme functionality.
  """
  # display_rules()
  place_ships(user=True, test=True)
  # print_board(boards["user"])
  place_ships(user=False)
  # print_board(boards["computer"])
  game_loop()
  # turn(user=True)

main()