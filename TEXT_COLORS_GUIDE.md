# Complete Text Colors Guide 🎨

## 📍 **Location Map: Where to Find Each Text Color**

### 🎯 **1. MAIN TITLE & SUBTITLE**

**File**: `app.py` (lines 221-222)
```python
st.markdown('<h1 class="main-header">Research Impact Network Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.1rem; color: #a0aec0; margin-bottom: 3rem; font-weight: 300;">Mapping Research Pathways from Grant Funding to Breakthrough Treatments</p>', unsafe_allow_html=True)
```

**Colors**:
- **Main Title**: Defined in `style.css` line 12 → `color: #ffffff;` (White)
- **Subtitle**: Inline style → `color: #a0aec0;` (Light Grey)

---

### 🎯 **2. GLOBAL APP TEXT**

**File**: `style.css` (lines 2-5)
```css
.stApp {
    background-color: #0e1117;
    color: #fafafa;  /* 🎨 DEFAULT TEXT COLOR FOR ENTIRE APP */
}
```

**Color**: `#fafafa` (Very Light Grey) - This affects ALL text unless overridden

---

### 🎯 **3. NETWORK SELECTION CARDS**

**File**: `style.css` (lines 37-58)

#### **Card Title** (Disease names like "Cancer", "Diabetes")
```css
.network-title {
    font-size: 1.4rem;
    font-weight: 500;
    color: #e2e8f0;  /* 🎨 CARD TITLE COLOR */
    margin-bottom: 0.5rem;
}
```

#### **Treatment Name** (Like "CAR-T Cell Therapy")
```css
.treatment-name {
    font-size: 1.1rem;
    color: #90cdf4;  /* 🎨 TREATMENT NAME COLOR (Light Blue) */
    font-weight: 400;
    margin-bottom: 1rem;
}
```

#### **Card Details** (Grant ID, Duration info)
```css
.network-details {
    font-size: 0.9rem;
    color: #cbd5e0;  /* 🎨 CARD DETAILS COLOR (Medium Grey) */
    line-height: 1.6;
}
```

---

### 🎯 **4. SIDEBAR TEXT**

**File**: `app.py` (lines 227-229)
```python
st.sidebar.markdown("### Database Statistics")
st.sidebar.write(f"Total connections: {len(edges_df)}")
st.sidebar.write(f"Treatment pathways: {len(edges_df[edges_df['edge_type'] == EDGE_TYPE_LEADS_TO_TREATMENT])}")
```

**Color**: Uses global `#fafafa` from `.stApp` unless overridden by Streamlit's sidebar styling

---

### 🎯 **5. SECTION HEADERS**

**File**: `app.py` (various lines)
```python
st.markdown("## Network Selection")                    # Line ~235
st.markdown("### Available Research Networks")         # Line ~275  
st.markdown(f"## 📊 Network {network_id}: {selected_summary['disease']} Research Impact")  # Line ~326
st.markdown("### 🕸️ Research Network Visualization")  # Line ~329
```

**Color**: Uses global `#fafafa` from `.stApp`

---

### 🎯 **6. INSTRUCTION MESSAGE**

**File**: `app.py` (line ~299)
```python
st.info("👆 Please select a disease, treatment, or grant from the dropdown above to view available research networks.")
```

**Color**: Controlled by `style.css` lines 115-118
```css
.stInfo {
    background-color: rgba(66, 153, 225, 0.1);
    border: 1px solid #4299e1;
    border-radius: 8px;
}
```
Text color uses Streamlit's default info box styling (usually dark blue/black text)

---

### 🎯 **7. SUCCESS MESSAGES**

**File**: `app.py` (around line ~340)
```python
st.success(f"🎉 **Research Impact Confirmed!** ...")
```

**Color**: Controlled by `style.css` lines 121-125
```css
.stSuccess {
    background-color: rgba(72, 187, 120, 0.1);
    border: 1px solid #48bb78;
    border-radius: 8px;
}
```
Text color uses Streamlit's default success box styling

---

### 🎯 **8. BUTTON TEXT**

**File**: `style.css` (lines 128-182)
```css
.stButton > button,
button[data-testid="baseButton-primary"],
button[data-testid="baseButton-secondary"],
div[data-testid="stForm"] button {
    color: #ffffff !important;  /* 🎨 BUTTON TEXT COLOR (White) */
}
```

---

### 🎯 **9. DROPDOWN/SELECTBOX TEXT**

**File**: `style.css` (lines 108-112)
```css
.stSelectbox > div > div {
    background-color: #2d3748;
    border: 1px solid #4a5568;
    border-radius: 6px;
}
```
Text color inherits from global or Streamlit defaults

---

### 🎯 **10. VISUALIZATION CHART TEXT**

**File**: `app.py` (lines ~190-200 in create_network_visualization function)
```python
fig.update_layout(
    title={'text': f"Research Impact Network - Network {network_id}", 
           'font': {'size': 20, 'color': '#e2e8f0'}},  # 🎨 CHART TITLE COLOR
    font=dict(color='#e2e8f0'),  # 🎨 GENERAL CHART TEXT COLOR
    legend=dict(
        font=dict(size=11, color='#e2e8f0')  # 🎨 LEGEND TEXT COLOR
    )
)
```

---

## 🎨 **Quick Color Reference Table**

| Element | Location | Current Color | Hex Code | Description |
|---------|----------|---------------|----------|-------------|
| **App Default** | `style.css` line 4 | Very Light Grey | `#fafafa` | Base text color |
| **Main Title** | `style.css` line 12 | White | `#ffffff` | Page header |
| **Subtitle** | `app.py` line 222 | Light Grey | `#a0aec0` | Page subtitle |
| **Card Titles** | `style.css` line 41 | Light Grey | `#e2e8f0` | Disease names |
| **Treatment Names** | `style.css` line 47 | Light Blue | `#90cdf4` | Treatment names |
| **Card Details** | `style.css` line 53 | Medium Grey | `#cbd5e0` | Grant info |
| **Button Text** | `style.css` line 133 | White | `#ffffff` | All buttons |
| **Chart Title** | `app.py` line ~195 | Light Grey | `#e2e8f0` | Visualization title |
| **Chart Text** | `app.py` line ~205 | Light Grey | `#e2e8f0` | Chart labels |

---

## 🔧 **How to Change Colors - Examples**

### **Make Main Title RED:**
In `style.css` line 12, change:
```css
color: #ffffff;  /* FROM: White */
```
to:
```css
color: #ff4757;  /* TO: Red */
```

### **Make Treatment Names GOLD:**
In `style.css` line 47, change:
```css
color: #90cdf4;  /* FROM: Light Blue */
```
to:
```css
color: #ffa502;  /* TO: Gold */
```

### **Make Card Details BRIGHTER:**
In `style.css` line 53, change:
```css
color: #cbd5e0;  /* FROM: Medium Grey */
```
to:
```css
color: #ffffff;  /* TO: White */
```

### **Change Subtitle Color:**
In `app.py` line 222, change:
```python
color: #a0aec0;  # FROM: Light Grey
```
to:
```python
color: #63b3ed;  # TO: Blue
```

---

## 💡 **Pro Tips:**

1. **Start with `style.css`** - Most colors are defined there
2. **Global changes**: Modify `.stApp` color for app-wide text changes
3. **Test one at a time**: Change one color, save, refresh browser
4. **Use color picker tools**: Like [coolors.co](https://coolors.co) for hex codes
5. **Keep contrast in mind**: Ensure text is readable against dark backgrounds

---

## 🚀 **Quick Test:**
1. Open `style.css`
2. Change line 47: `color: #90cdf4;` to `color: #ff6b6b;` (red)
3. Save file
4. Refresh browser
5. Treatment names should now be red!
