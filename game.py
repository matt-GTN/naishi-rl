from naishi import GameState

game = GameState().create_initial_state()

game.show()

end = False
while not end:
    end = game.play()
    game.show()