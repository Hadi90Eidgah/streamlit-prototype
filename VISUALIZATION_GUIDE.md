# Streamlit Visualization Modification Guide

## Quick Setup for Live Development

### 1. Running the App Locally
```bash
# Navigate to your project directory
cd streamlit-prototype

# Run the app (it will auto-reload when you save changes)
streamlit run app.py
```

**Pro Tip**: Streamlit automatically reloads when you save files, so you'll see changes immediately!

## Key Visualization Components

### 1. Node Colors and Sizes (config.py)

**Location**: `config.py` lines 20-40

```python
NODE_COLORS = {
    'grant': '#4299e1',              # Blue - Change this for grant color
    'publication': '#a0aec0',        # Grey - General publications
    'treatment': '#38b2ac',          # Teal - Change this for treatment color
    'grant_funded_pub': '#718096',   # Dark grey - Grant-funded papers
    'treatment_pathway_pub': '#ed8936',  # Orange - Treatment papers
    'ecosystem_pub': '#718096'       # Light grey - Ecosystem papers
}

NODE_SIZES = {
    'grant': 30,                     # Make bigger/smaller
    'publication': 10,
    'treatment': 35,                 # Treatment node size
    'grant_funded_pub': 12,
    'treatment_pathway_pub': 15,     # Treatment pathway papers
    'ecosystem_pub': 8               # Ecosystem papers
}
```

**Quick Changes You Can Make**:
- Change `'grant': '#4299e1'` to `'grant': '#ff6b6b'` for red grants
- Change `'treatment': 35` to `'treatment': 50` for bigger treatment nodes
- Save the file and refresh your browser to see changes!

### 2. Edge Colors and Widths (config.py)

**Location**: `config.py` lines 42-60

```python
EDGE_COLORS = {
    'funded_by': 'rgba(74, 85, 104, 0.8)',        # Grey - Grant funding
    'leads_to_treatment': 'rgba(99, 179, 237, 0.9)',  # Blue - Impact pathway
    'cites': 'rgba(160, 174, 192, 0.25)',         # Light grey - Citations
    'enables_treatment': 'rgba(56, 178, 172, 0.8)' # Teal - Treatment enablement
}

EDGE_WIDTHS = {
    'funded_by': 3,              # Thickness of grant funding lines
    'leads_to_treatment': 3,     # Thickness of impact pathway lines
    'cites': 0.8,               # Thickness of citation lines
    'enables_treatment': 2       # Thickness of treatment enablement lines
}
```

**Quick Changes**:
- Change `'leads_to_treatment': 3` to `'leads_to_treatment': 6` for thicker impact lines
- Change `'funded_by': 'rgba(74, 85, 104, 0.8)'` to `'funded_by': 'rgba(255, 0, 0, 0.8)'` for red funding lines

### 3. Node Positioning (config.py)

**Location**: `config.py` lines 62-80

```python
NODE_POSITIONS_X = {
    'grant': -5,                    # Left side - grants
    'grant_funded_pub': -2.5,       # Left-center - grant papers
    'ecosystem_pub_cluster': [-0.5, 0.5, 1.5, 0],  # Center - ecosystem
    'treatment_pathway_pub': 3.5,   # Right-center - treatment papers
    'treatment': 6                  # Right side - treatments
}
```

**Quick Changes**:
- Change `'grant': -5` to `'grant': -7` to move grants further left
- Change `'treatment': 6` to `'treatment': 8` to move treatments further right

## Main Visualization Function

### Location: `app.py` lines 155-200 (create_network_visualization)

This is where the magic happens! Here are the key parts you can modify:

### 4. Figure Layout and Styling

**Location**: `app.py` around line 180-200

```python
fig.update_layout(
    title={'text': f"Research Impact Network - Network {network_id}", 
           'x': 0.5, 'xanchor': 'center', 
           'font': {'size': 20, 'color': '#e2e8f0'}},  # Title styling
    height=600,                    # Chart height - change this!
    xaxis=dict(range=[-6, 7]),     # X-axis range - adjust for wider/narrower
    yaxis=dict(range=[-3, 3]),     # Y-axis range - adjust for taller/shorter
    plot_bgcolor='rgba(14, 17, 23, 0)',  # Background color
    paper_bgcolor='rgba(14, 17, 23, 0)'  # Paper background
)
```

**Quick Changes**:
- Change `height=600` to `height=800` for taller charts
- Change `xaxis=dict(range=[-6, 7])` to `xaxis=dict(range=[-8, 10])` for wider view
- Change title `'size': 20` to `'size': 24` for bigger title

### 5. Node Creation Functions

**Location**: `app.py` lines 100-130

```python
def create_node_trace(nodes, node_positions, node_type, name, text_template, showlegend):
    # This function creates each type of node
    marker=dict(
        size=NODE_SIZES[node_type],           # Size from config
        color=NODE_COLORS[node_type],         # Color from config
        line=dict(width=2, color='#e2e8f0')   # Border - change this!
    )
```

**Quick Changes**:
- Change `line=dict(width=2, color='#e2e8f0')` to `line=dict(width=4, color='#ffffff')` for thicker white borders

## CSS Styling (style.css)

### 6. Card Styling

**Location**: `style.css` lines 18-28

```css
.selection-card { 
    background: linear-gradient(135deg, #1e2329 0%, #2d3748 100%);
    padding: 1.2rem; 
    border-radius: 8px; 
    border: 1px solid #4a5568; 
    max-width: 300px;
}
```

**Quick Changes**:
- Change `max-width: 300px` to `max-width: 400px` for wider cards
- Change `border-radius: 8px` to `border-radius: 15px` for more rounded corners

## Testing Your Changes

### Immediate Feedback Loop:

1. **Make a change** in any of the files above
2. **Save the file** (Ctrl+S)
3. **Go to your browser** where Streamlit is running
4. **Click "Always rerun"** when prompted, or manually refresh
5. **See your changes instantly!**

### Example Quick Test:

1. Open `config.py`
2. Change `'grant': '#4299e1'` to `'grant': '#ff0000'` (red)
3. Change `'treatment': 35` to `'treatment': 50`
4. Save the file
5. Refresh your browser - grants should now be red and treatments bigger!

## Common Modifications

### Make Impact Pathways More Prominent:
```python
# In config.py
EDGE_COLORS = {
    'leads_to_treatment': 'rgba(255, 215, 0, 1.0)',  # Gold color
}
EDGE_WIDTHS = {
    'leads_to_treatment': 5,  # Much thicker
}
```

### Change Network Layout:
```python
# In config.py - spread nodes further apart
NODE_POSITIONS_X = {
    'grant': -8,           # Further left
    'treatment': 10        # Further right
}
```

### Bigger Visualization:
```python
# In app.py, in the fig.update_layout() section
height=800,                    # Taller
xaxis=dict(range=[-10, 12]),   # Wider
```

## Pro Tips:

1. **Start Small**: Change one thing at a time to see the effect
2. **Use the Refresh Button**: The 🔄 button clears cache if data changes don't show
3. **Check the Console**: If something breaks, check the browser console for errors
4. **Backup First**: Make a copy of working code before big changes
5. **Use Git**: Commit working versions so you can revert if needed

## File Structure for Quick Reference:

```
streamlit-prototype/
├── app.py              # Main logic, visualization function
├── config.py           # Colors, sizes, positions - EASIEST TO MODIFY
├── style.css           # UI styling, cards, buttons
└── [data files]        # CSV/database files
```

**Start with `config.py` - it's the easiest place to make visual changes!**
