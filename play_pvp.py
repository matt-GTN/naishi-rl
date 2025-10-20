#!/usr/bin/env python3
"""
Convenience script to play Human vs Human.
Imports from src.gameplay.naishi_pvp
"""
from src.gameplay.naishi_pvp import NaishiPvP

if __name__ == "__main__":
    game = NaishiPvP()
    game.play()
