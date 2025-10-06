# Dropdown Text Colors Guide 🎯

## 📍 **Current Selectbox Styling Location**

**File**: `style.css` lines 121-126
```css
/* Selectbox styling */
.stSelectbox > div > div {
    background-color: #2d3748;    /* Box background */
    border: 1px solid #4a5568;    /* Box border */
    border-radius: 6px;
}
```

**❌ Missing**: Text color inside the dropdown boxes!

## 🎨 **The Text Color You're Looking For**

The **deep grey text** inside the dropdown boxes is currently using **Streamlit's default styling**. Here's where to control it:

### **1. Selected Value Text** (What shows in the closed dropdown)
```css
.stSelectbox > div > div > div {
    color: #your-color-here !important;
}
```

### **2. Dropdown Options Text** (When dropdown is open)
```css
.stSelectbox > div > div > div > div {
    color: #your-color-here !important;
}
```

### **3. More Specific Targeting** (Recommended)
```css
/* Target the selectbox input text */
.stSelectbox div[data-baseweb="select"] > div {
    color: #ffffff !important;  /* White text */
}

/* Target dropdown menu options */
.stSelectbox div[role="listbox"] div {
    color: #ffffff !important;  /* White text in dropdown */
    background-color: #2d3748 !important;  /* Dark background */
}

/* Target dropdown menu options on hover */
.stSelectbox div[role="listbox"] div:hover {
    color: #ffffff !important;
    background-color: #4299e1 !important;  /* Blue on hover */
}
```

## 🔧 **Complete Selectbox Styling (Copy & Paste)**

**Replace your current selectbox styling** in `style.css` (lines 121-126) with this:

```css
/* Complete Selectbox styling with text colors */
.stSelectbox > div > div {
    background-color: #2d3748 !important;
    border: 1px solid #4a5568 !important;
    border-radius: 6px !important;
    color: #ffffff !important;  /* 🎨 SELECTED VALUE TEXT COLOR */
}

/* Dropdown input text */
.stSelectbox div[data-baseweb="select"] > div {
    color: #ffffff !important;  /* 🎨 INPUT TEXT COLOR */
}

/* Dropdown arrow */
.stSelectbox div[data-baseweb="select"] svg {
    fill: #ffffff !important;  /* 🎨 ARROW COLOR */
}

/* Dropdown menu background */
.stSelectbox div[role="listbox"] {
    background-color: #2d3748 !important;
    border: 1px solid #4a5568 !important;
    border-radius: 6px !important;
}

/* Dropdown menu options */
.stSelectbox div[role="listbox"] div {
    color: #ffffff !important;  /* 🎨 DROPDOWN OPTIONS TEXT COLOR */
    background-color: #2d3748 !important;
    padding: 8px 12px !important;
}

/* Dropdown menu options on hover */
.stSelectbox div[role="listbox"] div:hover {
    color: #ffffff !important;  /* 🎨 HOVER TEXT COLOR */
    background-color: #4299e1 !important;  /* 🎨 HOVER BACKGROUND COLOR */
}
```

## 🎨 **Color Examples**

### **White Text (High Contrast)**
```css
color: #ffffff !important;
```

### **Light Blue Text**
```css
color: #90cdf4 !important;
```

### **Light Grey Text**
```css
color: #e2e8f0 !important;
```

### **Gold Text**
```css
color: #fbbf24 !important;
```

## 🚀 **Quick Test Steps:**

1. **Open `style.css`**
2. **Find lines 121-126** (current selectbox styling)
3. **Replace with the complete styling above**
4. **Save the file**
5. **Refresh your browser**
6. **Click on the dropdown** - text should now be white!

## 🎯 **Specific Lines to Change:**

If you want to keep your current styling and just add text color:

**Add these lines after line 126 in `style.css`:**
```css
/* Dropdown text colors */
.stSelectbox div[data-baseweb="select"] > div {
    color: #ffffff !important;  /* Selected value text */
}

.stSelectbox div[role="listbox"] div {
    color: #ffffff !important;  /* Dropdown options text */
}
```

## 💡 **Pro Tip:**
The reason the text appears "deep grey" is because Streamlit's default text color for dropdowns is designed for light backgrounds. Since you're using a dark theme, you need to explicitly set the text color to something lighter (like white) for better contrast!
