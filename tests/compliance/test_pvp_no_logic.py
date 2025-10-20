"""
Test Task 29: Verify naishi_pvp.py contains no game logic
- No action validation
- No emissary spot management
- No player switching
- No ending checks
- Pure delegation to GameState
"""

import ast
import inspect


def test_no_game_logic_in_naishi_pvp():
    """Verify naishi_pvp.py contains no game logic"""
    
    # Read the file
    with open('naishi_pvp.py', 'r') as f:
        content = f.read()
    
    # Parse AST
    tree = ast.parse(content)
    
    # Find NaishiPvP class
    naishi_pvp_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'NaishiPvP':
            naishi_pvp_class = node
            break
    
    assert naishi_pvp_class is not None, "NaishiPvP class not found"
    
    # Check methods
    methods = {node.name: node for node in naishi_pvp_class.body if isinstance(node, ast.FunctionDef)}
    
    print("\n=== Task 29: naishi_pvp.py Game Logic Audit ===\n")
    
    # 1. Check _offer_optional_emissary has no validation
    print("1. Checking _offer_optional_emissary()...")
    if '_offer_optional_emissary' in methods:
        method = methods['_offer_optional_emissary']
        method_source = ast.get_source_segment(content, method)
        
        # Should NOT check player.emissaries
        assert 'player.emissaries' not in method_source, \
            "_offer_optional_emissary should not check player.emissaries"
        
        # Should NOT check legal_types for emissary actions
        assert 'ACTION_SWAP in legal_types' not in method_source, \
            "_offer_optional_emissary should not validate legal action types"
        assert 'ACTION_DISCARD in legal_types' not in method_source, \
            "_offer_optional_emissary should not validate legal action types"
        
        # Should just ask the player
        assert 'get_choice' in method_source, \
            "_offer_optional_emissary should ask player for choice"
        
        print("   ✓ No emissary validation logic")
        print("   ✓ Pure UI delegation")
    
    # 2. Check play() has no ending checks
    print("\n2. Checking play() method...")
    if 'play' in methods:
        method = methods['play']
        method_source = ast.get_source_segment(content, method)
        
        # Should use terminated/truncated from GameState
        assert 'terminated' in method_source, \
            "play() should check terminated from GameState"
        assert 'truncated' in method_source, \
            "play() should check truncated from GameState"
        
        # Should NOT have custom ending logic
        assert 'if self.gs.river' not in method_source, \
            "play() should not check river state directly"
        
        print("   ✓ Uses GameState terminated/truncated")
        print("   ✓ No custom ending logic")
    
    # 3. Check _get_player_action has no validation
    print("\n3. Checking _get_player_action()...")
    if '_get_player_action' in methods:
        method = methods['_get_player_action']
        method_source = ast.get_source_segment(content, method)
        
        # Should query legal_types from GameState
        assert 'get_legal_action_types' in method_source, \
            "_get_player_action should query legal types from GameState"
        
        # Should NOT validate actions itself
        assert 'if player.emissaries' not in method_source, \
            "_get_player_action should not validate emissaries"
        
        print("   ✓ Queries legal actions from GameState")
        print("   ✓ No action validation logic")
    
    # 4. Check no player switching
    print("\n4. Checking for player switching logic...")
    # Should NOT have current_player_idx manipulation
    assert 'current_player_idx =' not in content or 'self.gs.current_player_idx' not in content, \
        "naishi_pvp should not manipulate current_player_idx"
    
    print("   ✓ No player switching logic")
    
    # 5. Check no emissary spot management
    print("\n5. Checking for emissary spot management...")
    assert 'emissary_spots' not in content, \
        "naishi_pvp should not manage emissary spots"
    
    print("   ✓ No emissary spot management")
    
    # 6. Verify delegation to GameState
    print("\n6. Checking delegation to GameState...")
    assert 'apply_action_array' in content, \
        "naishi_pvp should call apply_action_array"
    assert 'GameState.create_initial_state' in content, \
        "naishi_pvp should use GameState.create_initial_state"
    
    print("   ✓ Delegates to GameState.apply_action_array()")
    print("   ✓ Uses GameState.create_initial_state()")
    
    print("\n=== All Task 29 Checks Passed ===\n")
    print("Summary:")
    print("- No action validation in UI layer")
    print("- No emissary spot management")
    print("- No player switching logic")
    print("- No custom ending checks")
    print("- Pure delegation to GameState")


if __name__ == '__main__':
    test_no_game_logic_in_naishi_pvp()
    print("\n✓ Task 29 complete: naishi_pvp.py is pure UI wrapper")
