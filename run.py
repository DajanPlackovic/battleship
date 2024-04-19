# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high
from re import findall
from random import randint, choice, shuffle
import numpy as np
import os
from bidict import bidict

ships = {
    "carrier": 5,
    "battleship": 4,
    "cruiser": 3,
    "submarine": 3,
    "destroyer": 2
}

directions = {
    "N": np.array([-1, 0]),
    "S": np.array([1, 0]),
    "W": np.array([0, -1]),
    "E": np.array([0, 1])
}

dir_complements = {
    "N": "S",
    "S": "N",
    "W": "E",
    "E": "W"
}

direction_aliases = bidict({
    "U": "N",
    "D": "S",
    "L": "W",
    "R": "E"
})

messages = {
    True: {
        "ship": [
            "Uff! That one hurt!",
            "Yikes! Right in my ship!",
            "Ouch! Hope that wasn't my last one...",
            "Well, that one fought bravely...\nSunk bravely too..."
        ],
        "unmarked": [
            "Not even close! :)",
            "Miles off! Wrong ocean, even!",
            "You're making waves!\nOnly in the water, unfortunately. ;)",
            "Better luck next time.\nWait, why would I want that for you..."
        ],
        "previous": ""
    },
    False: {
        "ship": [
            "Yesss! Gotcha!",
            "Knew it! One down!",
            "So that's where you're hiding...",
            "Almost beat you.\nWait, is that right? I forgot to count."
        ],
        "unmarked": [
            "Oh, nothing there! Well, that's a bummer.",
            "Damn! Missed completely.",
            "Uff, gotta focus.",
            "Aha. So no ship there... Hmmm..."
        ],
        "previous": ""
    }
}

states = {
    "ship": "■",
    "orient": "□",
    "hit": "X",
    "miss": "O",
    "unmarked": "·"
}

columns = [chr(code) for code in range(65, 73)]
rows = [str(num) for num in range(1, 9)]


class Board():
    """
    Initializes a board:

    A dictionary with coordinate tuples as keys, field states as values
    and methods that allow actions upon the board.
    """

    def __init__(self, user=True, state=None):
        self.state = state if state else {}
        for i in range(8):
            for j in range(8):
                self.state[(i, j)] = {"point": "unmarked",
                                      "chains": [], "is_in_chain": False}

        self.chain_ends = []
        self.opponent = not user
        self.ship_count = sum(ships.values())

    def update_point(self, coordinates, new_state):
        """
        Updates the state of a point and saves that state as the last move.
        """
        self.state[coordinates]["point"] = new_state
        if new_state == "hit":
            self.ship_count -= 1
        if not self.opponent:
            self.update_chains(coordinates, new_state)

    def display_board(self):
        """
        Prints current state of the board with columns and rows indicated.
        """
        board_display = [list(['·'] * 8) for i in range(8)]
        for point in self.state:

            if self.opponent and self.state[point]["point"] == "ship":
                continue
            row, column = point
            board_display[row][column] = states[self.state[point]["point"]]

        return board_display

    def find_legitimate_directions(self, starting_square, ship):
        """
        Returns legitimate orientations for placing the ships, that do not go
        out of bounds or intersect an already placed ship.
        """
        legitimate_directions = []
        starting_square = np.array(starting_square)

        for direction in directions:
            counter = 0

            for idx in range(ships[ship]):
                move_square = starting_square + idx * directions[direction]
                if not all(0 <= move_square) or not all(move_square <= 7):
                    continue

                if self.state[tuple(move_square)]["point"] != "unmarked":
                    continue

                counter += 1

            if counter == ships[ship]:
                legitimate_directions.append(direction)

        if len(legitimate_directions) == 0:
            raise ValueError(
                "Ship cannot be placed in any orientation from the chosen "
                "starting position\nwithout overlapping another ship or going"
                " out of bounds.")

        return legitimate_directions

    def show_directions(self, start_square, legit_dirs, ship):
        """
        Displays the available orientations when placing ships.
        """
        start_square = np.array(start_square)

        self.state[tuple(start_square)]["point"] = "ship"

        for direction in legit_dirs:
            for idx in range(1, ships[ship]):
                ship_point = tuple(start_square + idx * directions[direction])
                self.state[ship_point]["point"] = "orient"

    def implement_direction(self, start_square, direction, legit_dirs, ship):
        """
        Accept direction input if legitimate, throw error if not legitimate.

        Returns True if the choice of starting coordinates should be reset,
        otherwise None.
        """
        direction = direction.upper()

        if direction in direction_aliases:
            direction = direction_aliases[direction]

        if not (direction in legit_dirs or direction == "C"):
            raise ValueError(
                f"{direction} is not one of the possible directions.")

        start_square = np.array(start_square)

        self.state = {
            point: {"point": "unmarked",
                    "chains": [],
                    "is_in_chain": False
                    }
            if state["point"] == "orient" else state
            for point, state in self.state.items()}

        if direction == "C":
            self.state[tuple(start_square)]["point"] = "unmarked"
            return True

        for idx in range(ships[ship]):
            self.state[tuple(start_square + idx *
                             directions[direction])]["point"] = "ship"

    def update_chains(self, starting_point, new_state):
        """
        Updates the info about chains of hits in the user's board
        after the computer makes its move.

        This info is later used by the computer to decide on its
        next move.
        """
        starting_point = np.array(starting_point)
        this_point = self.state[tuple(starting_point)]
        for direction in directions:
            try:
                next_point = self.state[tuple(
                    starting_point + directions[direction])]
            except Exception as e:
                continue
            if next_point["is_in_chain"]:
                extendable_chain = [chain for chain in next_point["chains"]
                                    if direction ==
                                    dir_complements[chain["end"]]]
                if len(extendable_chain):
                    extendable_chain = extendable_chain[0]
                    self.chain_ends = [chain_end for chain_end in
                                       self.chain_ends
                                       if chain_end["point"] !=
                                       tuple(starting_point) and
                                       chain_end["end"]
                                       != dir_complements[direction]]
                    if new_state == "miss":
                        continue
                    opposite_point = tuple(
                        starting_point + extendable_chain["length"] *
                        directions[direction]
                    )

                    extendable_chain["length"] += 1
                    this_point["chains"].append(extendable_chain.copy())
                    this_point["is_in_chain"] = True

                    perp_dirs = [dir for dir in directions.keys(
                    ) if dir != direction and
                        dir != dir_complements[direction]]

                    self.chain_ends = [ce for ce in
                                       self.chain_ends if ce["point"] ==
                                       opposite_point and not (ce["end"]
                                                               in perp_dirs
                                                               and
                                                               ce["length"] ==
                                                               1)
                                       ]

        if not this_point["is_in_chain"] and new_state == "hit":
            this_point["chains"].append(
                {"orientation": "NS", "length": 1, "end": "N"})
            this_point["chains"].append(
                {"orientation": "NS", "length": 1, "end": "S"})
            this_point["chains"].append(
                {"orientation": "WE", "length": 1, "end": "W"})
            this_point["chains"].append(
                {"orientation": "WE", "length": 1, "end": "E"})
            shuffle(this_point["chains"])
            this_point["is_in_chain"] = True

        chain_ends_elements = [
            {
                "point": tuple(starting_point),
                "length": chain["length"],
                "orientation": chain["orientation"],
                "end": chain["end"]
            } for chain in this_point["chains"] if chain["end"]
        ]
        self.chain_ends.extend(chain_ends_elements)

    def check_hit(self, target):
        """
        Check if the target was hit, update the board accordingly.

        Raise error if user retargets same spot.
        """
        row, column = target

        retarget_error = ValueError(
            "You already targeted that spot! Pick another one.\n\n⏎")

        if not self.opponent:
            target_string = columns[column] + rows[row]
            display_screen(
                f"Let's see... I think I'll go for {target_string}.")

        target_state = self.state[(row, column)]["point"]
        if target_state == "hit":
            raise retarget_error
        elif target_state == "miss":
            raise retarget_error
        elif target_state == "ship":
            self.update_point((row, column), "hit")
        elif target_state == "unmarked":
            self.update_point((row, column), "miss")

        message = choice(
            [text for text in messages[self.opponent][target_state]
                if text != messages[self.opponent]["previous"]])
        messages[self.opponent]["previous"] = message

        return message


boards = {
    "user": Board(),
    "computer": Board(user=False)
}


def display_screen(message, req_input=False, comp_d=True, ship_d=None):
    """
    Displays the message instructing the user on the next step,
    an input sign if input is expected and an enter sign in case
    none is and either the user's board or both the computer's and
    the user's board.
    """
    if ship_d:
        comp_d = False
    v_separator = "\n" + "=" * 80 + "\n"
    h_separator = " " * 4 + " | " + " " * 4
    padding = 0

    ship_names = [name for name in ships.keys()]

    print(v_separator)

    user_display = boards['user'].display_board()
    if comp_d:
        comp_display = boards['computer'].display_board()

    for idx in range(8):
        output = '  '.join([str(idx + 1), ' '.join(user_display[idx])])
        if comp_d or ship_d:
            output += h_separator
        padding = 40 - len(output)
        if comp_d:
            output += '  '.join([str(idx + 1), ' '.join(comp_display[idx])])
        elif ship_d:
            if idx in range(2, 7):
                if ship_d in ship_names:
                    ship_idx = ship_names.index(ship_d)
                    if idx < ship_idx + 2:
                        checkbox = states["orient"]
                    elif idx == ship_idx + 2:
                        checkbox = "☒"
                    else:
                        checkbox = states["ship"]
                else:
                    checkbox = states["ship"]
                ship = ship_names[idx - 2].capitalize()
                length = ships[ship_names[idx - 2]]
                output += f'  {checkbox} {ship}{" " * (10 - len(ship))}'
                output += f': Length {length}'
        print(" " * padding + output)

    output = '   ' + ' '.join([str(letter) for letter in columns])
    if comp_d or ship_d:
        output += h_separator
    padding = 40 - len(output)
    if comp_d:
        output += '   ' + ' '.join([str(letter) for letter in columns])

    print(" " * padding + output)

    print(v_separator)

    input_value = None

    if req_input:
        input_value = input(f"\n{message}\n\n====>\n")
    else:
        input(f"\n{message}\n\n⏎\n")

    os.system("clear")
    return input_value


def display_rules():
    """
    Show all the rules at the beginning of the game.
    """
    message = """Welcome to BATTLESHIP!

Whenever you see the symbol at the bottom of this message,
press enter to continue."""
    display_screen(message, comp_d=False)

    message = """Whenever you instead see the arrow below, you will be asked
to input something.

Type anything in and press Enter. Just don't leave it blank."""
    input_test = display_screen(message, req_input=True, comp_d=False)

    while len(input_test) == 0:
        input_test = display_screen(
            """See, that's the one thing that won't work. When you see
the arrow,you gotta type something.

Try again.""", req_input=True, comp_d=False)


# place_ships and its subfunctions

def parse_input(input):
    """
    Parses the input of a square for placing ships or targeting enemy ships.
    If the input is not valid, returns a ValueError.
    """
    processed_input = input.strip().replace(" ", "")
    try:
        if (len(processed_input) > 2):
            raise ValueError(
                "Input can contain only two characters (a letter A-H and "
                "a number 1-8) and spaces.\n"
                f"Input contains {len(processed_input)} characters.")

        column = findall(f"[{''.join(columns)}]", input.upper())

        if len(column) < 1:
            raise ValueError(
                "Input string should contain exactly one reference\n"
                "to a column (a letter from A to H or a to h).\n")

        row = findall(f"[{''.join(rows)}]", input)
        if len(row) < 1:
            raise ValueError(
                f"Input string should contain exactly one reference\n"
                "to a row (a number from 1 to 8).\n")

        return [int(row[0]) - 1, columns.index(column[0])]

    except Exception as e:
        raise ValueError(f"Input not accepted: {e}")


def dir_select(legit_dirs):
    message = ""

    line = "Choose the orientation of the ship by"
    line += (50 - len(line)) * " " + "| "
    if "N" in legit_dirs:
        line += f'{" " * 10}[U]p ↑ [N]orth'
    line += "\n"

    message += line

    line = "entering the first letter of a valid direction."
    line += (50 - len(line)) * " " + "| "
    line += "\n"

    message += line

    line = "Each direction has two alternative designations."
    line += (50 - len(line)) * " " + "| "

    if "W" in legit_dirs:
        line += f'[L]|[W] ←'
    else:
        line += " " * 15
    if "E" in legit_dirs:
        line += f' → [R]|[E]'
    line += "\n"

    message += line

    message += " " * 50 + "|" "\n"

    line = "Enter [C] to re-enter the starting [C]oordinate."
    line += (50 - len(line)) * " " + "| "
    if "S" in legit_dirs:
        line += f'{" " * 8}[D]own ↓ [S]outh'
    message += line

    return message


def place_ships(user, test=False):
    """
    When user is set to True, loops through the available ships and
    lets the user set them up on their board.

    When user is set to False, automatically generates the board
    setup for the computer.
    """
    board = boards["user"] if user else boards["computer"]

    if user and not test:
        display_screen(
            """Start by placing your ships. You can do so by first entering
a point on the board (e.g. A2) and then choosing an orientation.

The ship name and length will be shown before you are asked to
place it.""", comp_d=False)
        message = """
You will be asked to place the five ships you see above on your board.

The ships may not overlap, nor may they be placed\npartially outside the board.
"""
        display_screen(message,
                       comp_d=False, ship_d=True)
    if not user and not test:
        display_screen(
            """OK. Just give me a moment to place my ships as well...""",
            comp_d=True)

    for ship in ships:
        got_input = False
        while not (got_input):
            if user and not test:
                board.display_board()
                message = f"Place the {ship.capitalize()}:"
                message += f"Length {ships[ship]}\n\n"
                message += """You can do so by entering a column (A-H) and
a row (1-8) in any order."""
                start_square = display_screen(
                    message, req_input=True, ship_d=ship
                )
            else:
                start_square = [randint(0, 7), randint(0, 7)]
            try:
                if user and not test:
                    start_square = parse_input(start_square)
                legit_dirs = board.find_legitimate_directions(
                    start_square, ship
                )
            except Exception as e:
                if user and not test:
                    display_screen(e, comp_d=False, ship_d=ship)
                continue

            got_orientation = False
            while not (got_orientation):
                try:
                    if user and not test:
                        board.show_directions(
                            start_square, legit_dirs, ship)
                        chosen_dir = display_screen(
                            dir_select(legit_dirs),
                            req_input=True, comp_d=False, ship_d=ship
                        )
                    else:
                        chosen_dir = choice(legit_dirs)
                    reset = board.implement_direction(
                        start_square, chosen_dir, legit_dirs, ship)
                    if reset:
                        break
                    got_orientation = True
                except Exception as e:
                    if user and not test:
                        display_screen(e, comp_d=False, ship_d=ship)
                    continue

            if got_orientation:
                got_input = True
    if user and not test:
        display_screen("So this is your final board setup.", comp_d=False)


# game_loop and subfunctions
def computer_choose_target():
    """
    Chooses a target for the computer using info on previous hits.

    Identifies and corrects retargeting.
    """
    board = boards["user"]
    random_choice = [randint(0, 7), randint(0, 7)]

    while True:
        try:
            if len(board.chain_ends) == 0:
                return random_choice
                # return ( 3, 3 )
            target = board.chain_ends[-1]["point"] + \
                directions[board.chain_ends[-1]["end"]]
            if board.state[(target[0], target[1])]["point"] in ["hit", "miss"]:
                raise ValueError("retry")
            break
        except Exception as e:
            board.chain_ends = board.chain_ends[:-1]

    return (target[0], target[1])


def turn(user):
    """
    Processes a turn.

    If user is set to True, gets input from user and checks
    whether the chosen target is hit.

    If user is set to False, generates target for computer by
    invoking computer_choose_target and checks whether the chosen
    target is hit.
    """
    target_board = boards["computer"] if user else boards["user"]

    got_input = False
    while not got_input:
        if user:
            target = display_screen("Enter a field you would like to target.",
                                    req_input=True)
        else:
            target = computer_choose_target()
        try:
            if user:
                target = parse_input(target)
            message = target_board.check_hit(target)
            got_input = True
        except Exception as e:
            if user:
                display_screen(e)

    display_screen(message)


def victory_screen(user_lost):
    """
    Displays a victory or loss screen depending on the outcome of the game
    and prompts the user to restart the game.
    """
    if user_lost:
        print(r"""
 __  __     ______     __  __        __         ______     ______     ______
/\ \_\ \   /\  __ \   /\ \/\ \      /\ \       /\  __ \   /\  ___\   /\__  _\
\ \____ \  \ \ \/\ \  \ \ \_\ \     \ \ \____  \ \ \/\ \  \ \___  \  \/_/\ \/
 \/\_____\  \ \_____\  \ \_____\     \ \_____\  \ \_____\  \/\_____\    \ \_\
  \/_____/   \/_____/   \/_____/      \/_____/   \/_____/   \/_____/     \/_/
""")
        message = "Maybe you'll have better luck next time."
    else:
        print(r"""
 __  __     ______     __  __        __     __     ______     __   __
/\ \_\ \   /\  __ \   /\ \/\ \      /\ \  _ \ \   /\  __ \   /\ "-.\ \
\ \____ \  \ \ \/\ \  \ \ \_\ \     \ \ \/ ".\ \  \ \ \/\ \  \ \ \-.  \
 \/\_____\  \ \_____\  \ \_____\     \ \__/".~\_\  \ \_____\  \ \_\\"\_\
  \/_____/   \/_____/   \/_____/      \/_/   \/_/   \/_____/   \/_/ \/_/
""")
        message = "Wanna beat the computer again?"

    print(" " * (40 - len(message) // 2) + message)
    print(" " * 27 + "PRESS ENTER TO PLAY AGAIN")
    input()
    os.system("clear")


def game_loop():
    """
    Runs the main game loop.

    Alternates between user's and computer's turns until
    one of the boards has no ships remaining.
    """

    display_screen("""Let's play!

You can start by entering a coordinate, same as you did in the first step
when placing your ships, to target one of mine.

I'll let you know whether you hit or missed and then take my turn.""")
    user = True
    while boards["computer"].ship_count > 0 and boards["user"].ship_count > 0:
        turn(user)
        user = not user
    return user


def main():
    """
    Runs all of the programme functionality.
    """
    os.system("clear")
    while True:
        print(r"""
 ______  ______  ______  ______  __      ______  ______  __  __  __  ______
/\  == \/\  __ \/\__  _\/\__  _\/\ \    /\  ___\/\  ___\/\ \_\ \/\ \/\  == \
\ \  __<\ \  __ \/_/\ \/\/_/\ \/\ \ \___\ \  __\\ \___  \ \  __ \ \ \ \  _-/
 \ \_____\ \_\ \_\ \ \_\   \ \_\ \ \_____\ \_____\/\_____\ \_\ \_\ \_\ \_\
  \/_____/\/_/\/_/  \/_/    \/_/  \/_____/\/_____/\/_____/\/_/\/_/\/_/\/_/
""")
# taken from https://patorjk.com/software/taag/
        input(" " * 26 + "PRESS ENTER TO BEGIN\n")
        os.system("clear")
        display_rules()
        while True:
            place_ships(user=True)
            # place_ships(user=True, test=True)
            place_ships(user=False)
            user_lost = game_loop()
            victory_screen(user_lost)


main()
