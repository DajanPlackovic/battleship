m("clear")
#     while True:
#         print(r"""
#  ______  ______  ______  ______  __      ______  ______  __  __  __  ______
# /\  == \/\  __ \/\__  _\/\__  _\/\ \    /\  ___\/\  ___\/\ \_\ \/\ \/\  == \
# \ \  __<\ \  __ \/_/\ \/\/_/\ \/\ \ \___\ \  __\\ \___  \ \  __ \ \ \ \  _-/
#  \ \_____\ \_\ \_\ \ \_\   \ \_\ \ \_____\ \_____\/\_____\ \_\ \_\ \_\ \_\
#   \/_____/\/_/\/_/  \/_/    \/_/  \/_____/\/_____/\/_____/\/_/\/_/\/_/\/_/
# """)  # from https://patorjk.com/software/taag/#p=display&f=Sub-Zero&t=battleship
#         input(" " * 26 + "PRESS ENTER TO BEGIN\n")
#         os.system("clear")
#         display_rules()
#         while True:
#             place_ships(user=True)
#             # place_ships(user=True, test=True)
#             place_ships(user=False)
#             user_lost = game_loop()