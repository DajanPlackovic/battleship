# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from re import findall

counter = 0

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

userBoard = []
computerBoard = []

columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
rows = [str(num) for num in range(1,9)]

def parseInput(input):
  """
  Parses the input of a square for placing ships or targeting enemy ships.
  If the input is not valid, returns a ValueError.
  """
  processedInput = input.strip().replace(" ","")
  try:
    if (len(processedInput) > 2):
        raise ValueError(f"Input can contain only two characters (a letter A-H and a number 1-8) and spaces.\nInput contains {len(processedInput)} characters.")
    
    column = findall(f"[{''.join(columns)}]", input.upper())
    
    if len(column) < 1:
      raise ValueError(f"Input string should contain exactly one reference\nto column (a letter from A to H or a to h).\n")
    
    row = findall(f"[{''.join(rows)}]", input)
    if len(row) < 1:
      raise ValueError(f"Input string should contain exactly one reference\nto row (a number from 1 to 8).\n")
    
    return [ int(row[0]) - 1, columns.index(column[0]) ]
  
  except Exception as e:
    raise ValueError(f"Input not accepted: {e}\n\nPress any key to try again.\n")

def printBoard(board):
  """
  Prints current state of the board with columns and rows indicated.
  """
  boardDisplay = [ list(['·'] * 8) for i in range(8) ]
  for point in board:
    row, column, state = point
    boardDisplay[row][column] = states[state]

  for idx in range(len(boardDisplay)):
    print('  '.join([str(idx + 1), ' '.join(boardDisplay[idx])]))
  print('   ' + ' '.join([ str(letter) for letter in columns ]))

def findLegitimateDirections(board, startingSquare, shipLength):
  """
  Returns legitimate orientations for placing the ships, that do not go
  out of bounds or intersect an already placed ship.
  """
  legitimateDirections = []
  row, column = startingSquare

  for direction in directions:
    rowMod = directions[direction][0]
    colMod = directions[direction][1]

    counter = 0
                        
    for idx in range(shipLength):
      newRow = row + idx * rowMod
      if not(0 <= newRow <= 7):
        continue

      newCol = column + idx * colMod
      if not(0 <= newCol <= 7):
        continue

      if True in (point[0] == newRow and point[1] == newCol for point in board):
        continue
      
      counter += 1
    
    print(counter)
    if counter == shipLength:
        legitimateDirections.append(direction)
        

  if len(legitimateDirections) == 0:
    raise ValueError("Ship cannot be placed in any orientation from the chosen starting position\nwithout overlapping another ship or going out of bounds.\n\nPress any key to try again.")
  
  return legitimateDirections

def showDirections(board, startingSquare, legitimateDirections, shipLength):
  """
  Displays the available orientations when placing ships.
  """
  row, column = startingSquare

  boardOrientation = board[:]
  boardOrientation.append([row, column, "ship"])

  for direction in legitimateDirections:
    for idx in range(1, shipLength):
      boardOrientation.append([row + idx * directions[direction][0], column + idx * directions[direction][1], "orient"])

  return boardOrientation

def implementDirection(board, startingSquare, direction, legitimateDirections, shipLength):
  if not(direction in legitimateDirections):
    raise ValueError("Not one of the possible directions.")
  
  row, column = startingSquare
  
  for idx in range(shipLength):
    board.append([row + idx * directions[direction][0], column + idx * directions[direction][1], "ship"])
  

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
        startingSquare = parseInput(startingSquare)
        legitimateDirections = findLegitimateDirections(userBoard, startingSquare, ships[ship])
      except Exception as e:
        input(e)
        continue

      gotOrientation = False
      while not(gotOrientation):
        try:
          printBoard(showDirections(userBoard, startingSquare, legitimateDirections, ships[ship]))
          chosenDirection = input(f"Choose the orientation of the ship: [N]orth, [E]ast, [S]outh or [W]est.\nBased on the starting position, the following orientations are possible:\n{', '.join(legitimateDirections)}\n")
          implementDirection(userBoard, startingSquare, chosenDirection, legitimateDirections, ships[ship])
          gotOrientation = True
        except Exception as e:
          print(e)

      gotInput = True 

def main():
  """
  Runs all of the programme functionality.
  """
  placeShips()

main()