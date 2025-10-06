# Example Modifications for Quick Testing
# Copy these into your config.py to see immediate changes!

# === EXAMPLE 1: Make grants RED and treatments GOLD ===
NODE_COLORS_EXAMPLE_1 = {
    'grant': '#ff4757',              # Bright red grants
    'publication': '#a0aec0',        
    'treatment': '#ffa502',          # Gold treatments
    'grant_funded_pub': '#718096',   
    'treatment_pathway_pub': '#ed8936',  
    'ecosystem_pub': '#718096'       
}

# === EXAMPLE 2: Make everything BIGGER ===
NODE_SIZES_EXAMPLE_2 = {
    'grant': 45,                     # Much bigger grants
    'publication': 15,               # Bigger publications
    'treatment': 55,                 # Huge treatments
    'grant_funded_pub': 18,
    'treatment_pathway_pub': 22,     
    'ecosystem_pub': 12              
}

# === EXAMPLE 3: Thick, colorful connections ===
EDGE_COLORS_EXAMPLE_3 = {
    'funded_by': 'rgba(255, 71, 87, 0.8)',        # Red funding lines
    'leads_to_treatment': 'rgba(255, 165, 2, 1.0)',  # Gold impact lines
    'cites': 'rgba(160, 174, 192, 0.4)',         # More visible citations
    'enables_treatment': 'rgba(46, 213, 115, 0.8)' # Green enablement
}

EDGE_WIDTHS_EXAMPLE_3 = {
    'funded_by': 5,              # Much thicker
    'leads_to_treatment': 6,     # Very thick impact lines
    'cites': 1.5,               # Thicker citations
    'enables_treatment': 4       # Thick enablement
}

# === EXAMPLE 4: Spread out layout ===
NODE_POSITIONS_X_EXAMPLE_4 = {
    'grant': -8,                    # Further left
    'grant_funded_pub': -4,         # More spread
    'ecosystem_pub_cluster': [-1, 1, 3, 0.5],  # Wider spread
    'treatment_pathway_pub': 5,     # Further right
    'treatment': 9                  # Much further right
}

# === HOW TO USE THESE EXAMPLES ===
# 1. Copy any of the above dictionaries
# 2. Replace the corresponding section in config.py
# 3. Save the file
# 4. Refresh your browser
# 5. See the changes immediately!

# === QUICK TEST INSTRUCTIONS ===
"""
STEP 1: Open config.py
STEP 2: Replace NODE_COLORS with NODE_COLORS_EXAMPLE_1
STEP 3: Save the file (Ctrl+S)
STEP 4: Go to your browser and refresh
STEP 5: See red grants and gold treatments!

Then try the other examples one by one to see different effects.
"""
