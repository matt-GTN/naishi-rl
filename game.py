from naishi import GameState

game = GameState().create_initial_state()

game.show()
end = False
while end == False:
    end = game.play()
    game.show()
game.score()