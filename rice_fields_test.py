cards = [1, 0, 0, 0, 1, 
         1, 1, 0, 0, 0]

# Grid layout:
# 0  1  2  3  4  (top row - indices 0-4)
# 5  6  7  8  9  (bottom row - indices 5-9)

def get_adjacent_indices(idx, length):
    """Returns adjacent indices based on 2-row grid (5 columns)"""
    adjacents = []
    cols = 5
    
    if idx < cols:  # Top row (0-4)
        if idx > 0: adjacents.append(idx - 1)           # left
        if idx < cols - 1: adjacents.append(idx + 1)    # right
        adjacents.append(idx + cols)                     # below (always valid for top row)
    else:  # Bottom row (5-9)
        if idx > cols: adjacents.append(idx - 1)        # left
        if idx < length - 1: adjacents.append(idx + 1)  # right
        adjacents.append(idx - cols)                     # above (always valid for bottom row)
    
    return adjacents

fields_groups = []
scoring_fields = []
processed = set()

for i, card in enumerate(cards):
    if card == 1 and i not in processed:
        # BFS/DFS to find all connected cards
        group = []
        stack = [i]
        
        while stack:
            current = stack.pop()
            if current in processed:
                continue
            
            processed.add(current)
            group.append(current)
            
            # Check all adjacent positions
            for adj_idx in get_adjacent_indices(current, len(cards)):
                if cards[adj_idx] == 1 and adj_idx not in processed:
                    stack.append(adj_idx)
        
        group.sort()
        scoring_fields.extend(group)
        fields_groups.append(len(group))

print(scoring_fields)  # [0, 4, 5, 6]
print(fields_groups)   # [4]