# naishi_core/utils.py

from .constants import LEFT_BOUNDARY, RIGHT_BOUNDARY, LINE_SIZE


def check_adjacency(position, cards):
    """
    Check which cards are adjacent to the given position.
    
    The board layout is:
        Line:  0  1  2  3  4
        Hand:  5  6  7  8  9
    
    Args:
        position: Index of the card (0-9)
        cards: List of 10 cards (line + hand)
    
    Returns:
        Dict with 'left', 'right', 'up', 'down' keys where applicable.
        Each value is a dict with 'card' and 'position' keys.
    
    Examples:
        >>> cards = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        >>> check_adjacency(0, cards)
        {'right': {'card': 'B', 'position': 1}, 'down': {'card': 'F', 'position': 5}}
        >>> check_adjacency(7, cards)
        {'left': {'card': 'G', 'position': 6}, 'right': {'card': 'I', 'position': 8}, 'up': {'card': 'C', 'position': 2}}
    """
    adjacents = {}
    
    # Left neighbor exists if not in leftmost column (positions 0 or 5)
    if position not in LEFT_BOUNDARY:
        adjacents['left'] = {
            'card': cards[position - 1],
            'position': position - 1
        }
    
    # Right neighbor exists if not in rightmost column (positions 4 or 9)
    if position not in RIGHT_BOUNDARY:
        adjacents['right'] = {
            'card': cards[position + 1],
            'position': position + 1
        }
    
    # Down neighbor exists if in top row (line: positions 0-4)
    if position < LINE_SIZE:
        adjacents['down'] = {
            'card': cards[position + LINE_SIZE],
            'position': position + LINE_SIZE
        }
    
    # Up neighbor exists if in bottom row (hand: positions 5-9)
    if position >= LINE_SIZE:
        adjacents['up'] = {
            'card': cards[position - LINE_SIZE],
            'position': position - LINE_SIZE
        }
    
    return adjacents


def get_choice(prompt, options):
    """
    Get validated integer input from user.
    
    Args:
        prompt: String to display to user
        options: List/range of valid integer choices
    
    Returns:
        The validated integer choice
    
    Example:
        >>> choice = get_choice("Pick a card (1-5): ", [1, 2, 3, 4, 5])
    """
    while True:
        try:
            choice = int(input(prompt))
            if choice in options:
                return choice
            else:
                print(f"Please enter only {list(options) if not isinstance(options, list) else options}.")
        except ValueError:
            print("Please enter a number.")
        except (KeyboardInterrupt, EOFError):
            print("\nGame interrupted.")
            raise