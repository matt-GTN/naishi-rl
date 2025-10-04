# game.py
# Entry point for human vs human play

from naishi_pvp import GameState

if __name__ == "__main__":
    game = GameState.create_initial_state()
    game.show()
    
    end = False
    while not end:
        end = game.play()
        game.show()
    
    game.score()