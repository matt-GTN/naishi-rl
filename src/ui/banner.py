from dataclasses import dataclass
from typing import List, Tuple

BLOCK, SPACE = "█", " "

LETTER_MAP = {
    "N": [
        "#     #","##    #","# #   #","#  #  #","#   # #","#    ##","#     #",
    ],
    "A": [
        "  ###  "," #   # ","#     #","#     #","#######","#     #","#     #",
    ],
    "I": [
        " ##### ","   #   ","   #   ","   #   ","   #   ","   #   "," ##### ",
    ],
    "S": [
        " ##### ","#     #","#      "," ####  ","      #","#     #"," ##### ",
    ],
    "H": [
        "#     #","#     #","#     #","#######","#     #","#     #","#     #",
    ],
}

def build_banner(text: str, spacing=2) -> List[str]:
    chars = [LETTER_MAP[ch] for ch in text.upper()]
    return [(" " * spacing).join(letter[row] for letter in chars) for row in range(7)]

def gradient(width: int, start: Tuple[int,int,int], end: Tuple[int,int,int]) -> List[Tuple[int,int,int]]:
    def lerp(a,b,t): return int(a+(b-a)*t)
    return [(lerp(start[0],end[0],i/(width-1)),
             lerp(start[1],end[1],i/(width-1)),
             lerp(start[2],end[2],i/(width-1))) for i in range(width)]

def color_block(r,g,b,ch): return f"\033[38;2;{r};{g};{b}m{ch}\033[0m"

def print_banner(text="NAISHI"):
    lines = build_banner(text)
    colors = gradient(len(lines[0]), (255,182,193), (199,21,133))  # pink → deep pink
    for line in lines:
        print("".join(color_block(*colors[i], BLOCK) if ch=="#" else SPACE
                      for i,ch in enumerate(line)))
