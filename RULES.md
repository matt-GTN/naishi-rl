# Naishi: Complete Game Rules

**Version:** 1.0  
**Last Updated:** October 19, 2025  
**For:** Human and AI players

---

## Table of Contents

1. [Game Overview](#game-overview)
2. [Setup](#setup)
3. [Game Components](#game-components)
4. [Turn Structure](#turn-structure)
5. [Actions](#actions)
6. [Emissary System](#emissary-system)
7. [Game End](#game-end)
8. [Scoring](#scoring)
9. [Card Details](#card-details)
10. [Strategy Tips](#strategy-tips)

---

## Game Overview

**Naishi** is a 2-player card game where players build a territory of 10 cards (5 in their Line, 5 in their Hand) by drawing from a shared River of 5 decks. Players use Emissaries to manipulate cards and must strategically position cards to maximize their score.

**Objective:** Have the highest score when the game ends.

**Game Length:** Typically 15-30 turns per player.

---

## Setup

### Initial Deal

1. **Shuffle all cards** (34 total cards)
2. **Deal River:** Create 5 decks of 6 cards each, face-down
3. **Deal starting hands:** Each player receives 2 random cards
4. **Draft phase:** 
   - Players view the top card of each River deck
   - Each player chooses 1 of their 2 cards to give to their opponent
   - Cards are exchanged simultaneously
5. **Add Mountains:** Each player receives 3 Mountain cards, shuffled into their hand
6. **Initialize Line:** Each player starts with 5 Mountains in their Line

**Final starting state:**
- Each player: 5 cards in Hand, 5 Mountains in Line
- River: 5 decks of 6 cards each

### Starting Player

Player 1 goes first (randomly determined or by agreement).

---

## Game Components

### The Board

Each player has:
- **Line:** 5 card positions (visible to both players)
- **Hand:** 5 card positions (hidden from opponent)

Layout:
```
Line:  [0] [1] [2] [3] [4]
Hand:  [5] [6] [7] [8] [9]
```

### The River

5 decks of cards, shared by both players:
```
Deck 1  Deck 2  Deck 3  Deck 4  Deck 5
[Top]   [Top]   [Top]   [Top]   [Top]
```

Only the top card of each deck is visible.

### Emissaries

Each player starts with **2 Emissaries** (represented as tokens or counters).

**Emissary Tracking Board:**
```
Swaps:     [ ] [ ] [ ]  (3 spots)
Discards:  [ ] [ ]      (2 spots)
Decree:    [ ]          (1 spot, shared)
```

When an Emissary is used, a marker (X for Player 1, O for Player 2) is placed in an available spot.

---

## Turn Structure

On your turn, you must choose ONE of the following actions:

1. **Develop Territory** (required action, can be combined with Emissary)
2. **Send an Emissary** (requires Develop Territory afterward)
3. **Recall Emissaries**
4. **Impose Imperial Decree**
5. **Declare End of Game** (only available when 1+ River decks are empty)

### Action Flow

**Option A: Develop First**
1. Develop Territory
2. Optionally: Send an Emissary (if you have one available)

**Option B: Emissary First**
1. Send an Emissary
2. Must: Develop Territory

**Option C: Other Actions**
- Recall Emissaries (ends turn)
- Impose Decree (ends turn)
- Declare End (ends game)

---

## Actions

### 1. Develop Territory

**Purpose:** Replace one of your cards with a card from the River.

**How to:**
1. Choose one card from your Line or Hand to discard (position 0-9)
2. The top card from the River deck at the **same position** is drawn
3. The drawn card replaces the discarded card

**Position Mapping:**
- Positions 0-4 (Line) → Draw from River Decks 0-4
- Positions 5-9 (Hand) → Draw from River Decks 0-4 (5→Deck 0, 6→Deck 1, 7→Deck 2, 8→Deck 3, 9→Deck 4)

**Rules:**
- The River deck at that position must not be empty
- The new card goes to the exact position of the discarded card
- This action is required on every turn (unless you Recall, Decree, or End)

**Example:**
```
Your Hand: [Mountain, Naishi, Fort, Monk, Torii]
           Position: 5, 6, 7, 8, 9
You discard: Position 6 (Naishi)
You draw from: Deck 1 (position 6 % 5 = 1) → Knight
Your Hand: [Mountain, Knight, Fort, Monk, Torii]
```

---

### 2. Send an Emissary

**Purpose:** Manipulate cards before or after developing.

**Requirements:**
- Must have at least 1 Emissary available
- Must Develop Territory on the same turn

**Two Emissary Actions:**

#### A. Swap Cards

Choose one of 4 swap types:

**i. Swap in Hand**
- Swap any 2 cards in your Hand
- Example: Swap Hand[0] with Hand[3]

**ii. Swap in Line**
- Swap any 2 cards in your Line
- Example: Swap Line[1] with Line[4]

**iii. Swap Between Hand and Line**
- Swap cards at the same position between Hand and Line
- Example: Swap Hand[2] with Line[2]

**iv. Swap in River**
- Swap the top cards of any 2 River decks
- Both decks must be non-empty
- Example: Swap top of Deck 1 with top of Deck 4

**Emissary Tracking:**
- When you use a Swap, place your marker in one of the 3 Swap spots
- If all 3 spots are filled, no more Swaps can be performed until someone Recalls
- Recalling your Emissaries clears your markers, freeing up spots

#### B. Discard River Cards

**How to:**
1. Choose 2 different River decks
2. Discard the top card from each deck
3. Those cards are removed from the game

**Rules:**
- Must choose 2 different decks
- Empty decks are skipped (no error)
- Useful for removing undesirable cards

**Emissary Tracking:**
- When you use a Discard, place your marker in one of the 2 Discard spots
- If both spots are filled, no more Discards can be performed until someone Recalls
- Recalling your Emissaries clears your markers, freeing up spots

---

### 3. Recall Emissaries

**Purpose:** Get your Emissaries back.

**How to:**
- Declare Recall
- All your Emissaries return to you
- Remove your markers from Swap and Discard spots
- Turn ends

**Rules:**
- Can only recall if you have fewer than your maximum Emissaries
- Normal maximum: 2 Emissaries
- If you used Decree: maximum is 1 Emissary (one is permanently locked)

**Example:**
```
You have: 0 Emissaries
You Recall: 2 Emissaries return (if no Decree used)
            1 Emissary returns (if Decree was used)
```

---

### 4. Impose Imperial Decree

**Purpose:** Swap one of your cards with your opponent's card at the same position.

**How to:**
1. Choose one of your cards (position 0-9)
2. That card is swapped with your opponent's card at the same position
3. Your Emissary is consumed
4. Turn ends

**Rules:**
- Requires 1 Emissary
- Can only be used ONCE per game (by either player)
- Once used, that Emissary is permanently locked
- After Decree, Recall can only restore 1 Emissary (not 2)
- Position mapping:
  - 0-4: Line positions
  - 5-9: Hand positions (5→Hand[0], 6→Hand[1], etc.)

**Example:**
```
Your Line[2]: Fort
Opponent Line[2]: Naishi
After Decree on position 2:
Your Line[2]: Naishi
Opponent Line[2]: Fort
```

**Important:** The Decree locks one Emissary permanently. Even after Recall, you can only have 1 Emissary for the rest of the game.

---

### 5. Declare End of Game

**Purpose:** End the game when you're ready.

**Requirements:**
- At least 1 River deck must be empty
- This option only appears when the condition is met

**How to:**
- Declare End
- Your opponent gets one final turn
- Game then proceeds to scoring

**Rules:**
- Declaring End always gives your opponent one last turn
- If you don't declare End, the game continues
- Game automatically ends when 2+ decks are empty (after Player 1's turn, giving Player 2 a final turn)

---

## Emissary System

### Starting Emissaries

Each player starts with **2 Emissaries**.

### Using Emissaries

Emissaries are consumed when you:
- Swap cards (any type)
- Discard River cards
- Impose Decree

### Emissary Limits

**Swap Spots:** 3 total (shared between players)
- Once all 3 spots are filled, no more Swaps can be performed
- Spots are cleared when players Recall their Emissaries
- There is no maximum number of total Swaps per game - spots can be reused

**Discard Spots:** 2 total (shared between players)
- Once both spots are filled, no more Discards can be performed
- Spots are cleared when players Recall their Emissaries
- There is no maximum number of total Discards per game - spots can be reused

**Decree:** 1 use per game (shared between players)
- Once used by either player, cannot be used again
- Permanently locks 1 Emissary for the player who used it

### Recalling Emissaries

**Without Decree:**
- Recall restores you to 2 Emissaries
- Clears your markers from Swap and Discard spots

**With Decree (after you used it):**
- Recall restores you to 1 Emissary only
- One Emissary is permanently locked
- Clears your markers from Swap and Discard spots

### Emissary Strategy

- **Conservation:** Don't waste Emissaries early
- **Timing:** Use Emissaries when they provide maximum benefit
- **Recall:** Recall when you need Emissaries back
- **Decree:** Very powerful but locks an Emissary forever

---

## Game End

### Ending Conditions

The game ends when:

1. **Player declares End** (when 1+ decks empty)
2. **Automatic End:** 2+ River decks are empty after Player 1's turn

### End Sequence

When 2+ decks become empty:
- If it's Player 2's turn: game ends immediately
- If it's Player 1's turn: Player 2 gets one final turn, then game ends

This ensures both players get equal turns.

---

## Scoring

### Scoring Process

1. **Resolve Ninjas:** Each Ninja copies another character card
2. **Calculate Scores:** Use scoring rules for each card type
3. **Determine Winner:** Highest score wins
4. **Tiebreaker:** Most unique cards (excluding Mountain and Ninja)

### Card Scoring Rules

#### Mountain
- **1 Mountain:** +5 points
- **2+ Mountains:** -5 points total

#### Naishi (Character)
- **Position 2 (Line center):** +12 points
- **Position 7 (Hand center):** +8 points
- **Other positions:** 0 points

#### Councellor (Character)
- **Positions 1, 3, 6, 8:** +4 points
- **Positions 2, 7:** +3 points
- **Positions 0, 4, 5, 9:** +2 points
- **Adjacent to Naishi:** +4 points (per Naishi)

#### Sentinel (Character)
- **Not adjacent to another Sentinel:** +3 points
- **Adjacent to Fort:** +4 points (per Fort)

#### Fort (Building)
- **Corner positions (0, 4, 5, 9):** +6 points
- **Other positions:** 0 points

#### Monk (Character)
- **In Hand (positions 5-9):** +5 points
- **Adjacent to Torii:** +2 points (per Torii)

#### Torii (Building)
- **1 Torii:** -5 points
- **2 Toriis:** 0 points
- **3+ Toriis:** +30 points total

#### Knight (Character)
- **In Hand (positions 5-9):** +3 points
- **Directly below Banner (Banner in Line, Knight in Hand at same column):** +10 points

#### Banner (Building)
- **1 Banner:** +3 points
- **2 Banners:** +8 points total
- **3+ Banners:** +8 points total (no additional bonus)

#### Rice Fields (Building)
- **Connected groups:** Score based on group size
  - 1 Rice Field (alone): 0 points
  - 2 connected: +10 points
  - 3 connected: +20 points
  - 4+ connected: +30 points (maximum)

**Adjacency:** Rice Fields are connected if they're adjacent (left, right, up, or down).

**Note:** The maximum score for any Rice Fields group is 30 points, regardless of size.

#### Ronin (Character)
- **Depends on unique card types** (excluding Mountain)
  - 8 unique types: +8 points per Ronin
  - 9 unique types: +15 points per Ronin
  - 10 unique types: +45 points per Ronin
- **Fewer than 8 unique:** 0 points

#### Ninja (Character)
- **Copies another character card** (chosen by player)
- Cannot copy another Ninja
- Cannot copy non-character cards
- Scores as the copied card

---

## Card Details

### Card Distribution

| Card | Count | Type |
|------|-------|------|
| Naishi | 2 | Character |
| Councellor | 4 | Character |
| Sentinel | 4 | Character |
| Monk | 3 | Character |
| Knight | 2 | Character |
| Ronin | 2 | Character |
| Fort | 4 | Building |
| Torii | 4 | Building |
| Banner | 2 | Building |
| Rice Fields | 5 | Building |
| Ninja | 2 | Character |
| **Total** | **34** | |

**Note:** Mountains are not in the deck; they're added during setup (3 per player).

### Character Cards

Can be copied by Ninja:
- Naishi
- Councellor
- Sentinel
- Monk
- Knight
- Ronin

### Building Cards

Cannot be copied by Ninja:
- Fort
- Torii
- Banner
- Rice Fields

### Special Cards

- **Mountain:** Starting card, affects scoring
- **Ninja:** Copies another character card

---

## Adjacency Rules

### Adjacent Positions

Cards are adjacent if they're directly next to each other (left, right, up, or down). Diagonal does NOT count.

```
Line:  [0] [1] [2] [3] [4]
        |   |   |   |   |
Hand:  [5] [6] [7] [8] [9]
```

**Examples:**
- Position 0 is adjacent to: 1 (right), 5 (down)
- Position 2 is adjacent to: 1 (left), 3 (right), 7 (down)
- Position 7 is adjacent to: 6 (left), 8 (right), 2 (up)
- Position 9 is adjacent to: 8 (left), 4 (up)

### Cards Affected by Adjacency

- **Councellor:** Bonus if adjacent to Naishi
- **Sentinel:** Penalty if adjacent to another Sentinel, bonus if adjacent to Fort
- **Monk:** Bonus if adjacent to Torii
- **Knight:** Bonus if directly below Banner (Banner in Line, Knight in Hand)
- **Rice Fields:** Connected groups score together

---



---

## Quick Reference

### Turn Actions

| Action | Emissary Cost | Ends Turn | Notes |
|--------|---------------|-----------|-------|
| Develop Territory | 0 | Yes | Required action |
| Swap Cards | 1 | No* | Must Develop after |
| Discard River | 1 | No* | Must Develop after |
| Recall Emissaries | 0 | Yes | Restores Emissaries |
| Impose Decree | 1 | Yes | Once per game |
| Declare End | 0 | Game Ends | Requires 1+ empty deck |

*Must be followed by Develop Territory on the same turn.

### Emissary Limits

- Starting: 2 per player
- Swap spots: 3 total (shared)
- Discard spots: 2 total (shared)
- Decree: 1 use per game (shared)
- After Decree: Max 1 Emissary (for user)

### Scoring Quick Reference

| Card | Key Scoring | Max Points |
|------|-------------|------------|
| Naishi | Position 2 | +12 |
| Councellor | Adjacent to Naishi | +4 per Naishi |
| Sentinel | Adjacent to Fort | +4 per Fort |
| Fort | Corners | +6 |
| Monk | In Hand + Torii | +5 + 2 per Torii |
| Torii | 3+ Toriis | +30 |
| Knight | Hand + below Banner | +3 + 10 |
| Banner | 2 Banners | +8 |
| Rice Fields | 4+ connected | +30 (max) |
| Ronin | 10 unique types | +45 per Ronin |
| Mountain | Exactly 1 | +5 |

---

## Frequently Asked Questions

**Q: Can I use 2 Emissaries on the same turn?**
A: No, you can only use 1 Emissary per turn.

**Q: What happens if all Swap spots are filled?**
A: No more Swaps can be performed until someone Recalls their Emissaries.

**Q: Can I Recall if I have 2 Emissaries?**
A: No, you can only Recall if you have fewer than your maximum.

**Q: Does Decree lock an Emissary for both players?**
A: No, only for the player who used it. The opponent keeps their 2 Emissaries.

**Q: Can Ninja copy a building card?**
A: No, Ninja can only copy character cards (Naishi, Councellor, Sentinel, Monk, Knight, Ronin).

**Q: What if there's a tie in score?**
A: The player with more unique card types wins. If still tied, it's a true tie.

**Q: Can I swap cards in an empty River deck?**
A: No, both decks must be non-empty for River swaps.

**Q: Do diagonal cards count as adjacent?**
A: No, only left, right, up, and down count as adjacent.

**Q: Can I end the game before any deck is empty?**
A: No, at least 1 deck must be empty to declare End.

**Q: What happens if I use Decree and then Recall?**
A: You only get 1 Emissary back (the other is permanently locked).

---

---

## Appendix: Position Reference

### Board Layout
```
        Line (visible to both players)
        ┌────┬────┬────┬────┬────┐
        │ 0  │ 1  │ 2  │ 3  │ 4  │
        └────┴────┴────┴────┴────┘
        ┌────┬────┬────┬────┬────┐
        │ 5  │ 6  │ 7  │ 8  │ 9  │
        └────┴────┴────┴────┴────┘
        Hand (hidden from opponent)
```

### Position Properties

| Position | Location | Corner | Center | Edge |
|----------|----------|--------|--------|------|
| 0 | Line | Yes | No | Left |
| 1 | Line | No | No | No |
| 2 | Line | No | Yes | No |
| 3 | Line | No | No | No |
| 4 | Line | Yes | No | Right |
| 5 | Hand | Yes | No | Left |
| 6 | Hand | No | No | No |
| 7 | Hand | No | Yes | No |
| 8 | Hand | No | No | No |
| 9 | Hand | Yes | No | Right |

---

**End of Rules**

For implementation details, see:
- `naishi_core/` - Core game logic
- `naishi_complex_env.py` - RL environment
- `naishi_pvp.py` - Human vs Human gameplay
