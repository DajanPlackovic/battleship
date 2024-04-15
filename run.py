# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from re import findall

ships = {
  "carrier" : 5,
  "battleship": 4,
  "cruiser": 3,
  "submarine": 3,
  "destroyer": 2
}

userBoard = [['·'] * 8] * 8
computerBoard = [['·'] * 8] * 8

columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
rows = [str(num) for num in range(1,9)]

def validateInput(input):
  """
  Validates the input of a square for placing ships or targeting enemy ships.
  """
  processedInput = input.strip().replace(" ","")
  try:
    if (len(processedInput) > 2):
        raise ValueError(f"Input can contain only two characters (a letter A-H and a number 1-8) and spaces.\nInput contains {len(processedInput)} characters.")
    
    column = findall(f"[{''.join(columns)}]", input.upper())
    
    if len(column) > 1:
      raise ValueError("Input string should contain exactly one reference\nto column (a letter from A to H or a to h).")
    
    row = findall(f"[{''.join(rows)}]", input)
    if len(row) > 1:
      raise ValueError("Input string should contain exactly one reference\nto row (a number between 1 and 8)")
    
  except Exception as e:
    raise ValueError(f"Input not accepted: {e}\n\nPress any key to try again.\n")

def printBoard(board):
  """
  Prints current state of the board with columns and rows indicated.
  """
  for idx in range(len(board)):
    print('  '.join([str(idx + 1), ' '.join(board[idx])]))
  print('   ' + ' '.join([ str(letter) for letter in columns ]))

def placeShips():
  """
  Loops through the five available ships and lets the player place them on the grid.
  """
  input(
"""
Start by placing your ships. You can do so by first entering a point
on the board (e.g. A2) and then choosing an orientation (N, E, S, W).

Press any key to continue.
""")
  for ship in ships:
    gotInput = False
    while not(gotInput):
      printBoard(userBoard)
      startingSquare = input(f"Place the {ship.capitalize()}: Length {ships[ship]}\n")
      try:
        validateInput(startingSquare)
        gotInput = True
      except Exception as e:
        input(e)
        gotInput = False

def main():
  """
  Runs all of the programme functionality.
  """
  placeShips()

main()