# naishi_core/constants.py

# Board configuration constants
BOARD_SIZE = 10
LINE_SIZE = 5
HAND_SIZE = 5
NUM_DECKS = 5
CARDS_PER_DECK = 6

# Position boundaries for adjacency checking
LEFT_BOUNDARY = {0, 5}  # Leftmost column positions
RIGHT_BOUNDARY = {4, 9}  # Rightmost column positions
HAND_START = 5  # First position in hand (cards 0-4 are line, 5-9 are hand)

# Player constants
PLAYER_1 = 0
PLAYER_2 = 1
NUM_PLAYERS = 2

# Card definitions
CARDS = [
    "Naishi", 
    "Councellor", 
    "Sentinel", 
    "Fort", 
    "Monk", 
    "Torii",
    "Knight",
    "Banner",
    "Rice fields",
    "Ronin",
    "Ninja"
]

CHARACTERS = [
    "Naishi", 
    "Councellor", 
    "Sentinel",  
    "Monk", 
    "Knight",
    "Ronin",
]

CARDS_COUNT = [2, 4, 4, 4, 3, 4, 2, 2, 5, 2, 2]

# Card encoding for RL (maps card name to integer)
CARD_TO_INT = {card: i for i, card in enumerate(CARDS)}
CARD_TO_INT['Mountain'] = len(CARDS)
CARD_TO_INT['Empty'] = len(CARDS) + 1

INT_TO_CARD = {i: card for card, i in CARD_TO_INT.items()}

# Emissary constants
INITIAL_EMISSARIES = 2
MAX_SWAPS = 3
MAX_DISCARDS = 2

# Display colors
PLAYER_COLORS = ['magenta', 'yellow']
RIVER_COLOR = 'blue'