import streamlit as st
import pandas as pd
import json
from streamlit_agraph import agraph, Node, Edge, Config

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Research Lineage Explorer: Givinostat",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SIDEBAR CONTROLS
# ============================================================
st.sidebar.header("⚙️ Controls")
selected_treatment = st.sidebar.selectbox(
    "Select Treatment:",
    ["Givinostat"]
)

max_layers = st.sidebar.slider(
    "Number of citation layers to visualize:",
    min_value=1, max_value=4, value=4
)

highlight_ft = st.sidebar.checkbox(
    "Highlight Fondazione Telethon-funded papers", value=True
)

show_table = st.sidebar.checkbox(
    "Show table below graph", value=False
)

st.sidebar.markdown("---")
st.sidebar.markdown("👋 *Interact with the graph: drag, zoom, hover for details.*")

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    with open("mock_graph.json", "r") as f:
        graph_data = json.load(f)
    df_nodes = pd.read_csv("mock_nodes.csv")
    df_edges = pd.read_csv("mock_edges.csv")
    return graph_data, df_nodes, df_edges

graph_data, df_nodes, df_edges = load_data()

# ============================================================
# FILTER DATA BY LAYER
# ============================================================
df_filtered = df_nodes[df_nodes["layer"] <= max_layers].copy()
filtered_ids = set(df_filtered["pubmed_id"].tolist())
df_edges = df_edges[df_edges["target"].isin(filtered_ids)]

# ============================================================
# HEADER & METRICS
# ============================================================
st.title("🔬 Research Lineage Explorer: Givinostat")
st.markdown(
    """
    Mapping how **Fondazione Telethon-funded research** contributed to the 
    FDA/EMA approval of **Givinostat** in treating Duchenne Muscular Dystrophy.
    """
)

col1, col2, col3 = st.columns(3)
col1.metric("Total Papers", len(df_filtered))
col2.metric("FT Funded", df_filtered["funding_source"].eq("Fondazione Telethon").sum())
col3.metric("Layers", max_layers)

st.markdown("---")

# ============================================================
# CREATE GRAPH ELEMENTS
# ============================================================

def color_for_node(row):
    """Assign node color based on type or funding."""
    if row["funding_source"] == "Fondazione Telethon":
        return "#2A9D8F"  # green-turquoise
    elif row["layer"] == 1:
        return "#457B9D"  # deep blue
    elif row["layer"] == 4:
        return "#A8DADC"  # soft teal
    elif row["layer"] == 5:
        return "#6D597A"  # FT grant
    else:
        return "#CCCCCC"  # default gray

def make_label(row):
    """Create concise label text for hover tooltips."""
    label = f"{row['title']}\nYear: {row['year']}"
    if pd.notna(row["funding_source"]):
        label += f"\nFunding: {row['funding_source']}"
    return label

nodes = []
edges = []

# Treatment node
treatment_node = Node(
    id="GIVINOSTAT",
    label="Givinostat (Treatment)",
    size=40,
    color="#E63946"
)
nodes.append(treatment_node)

# Publication nodes
for _, row in df_filtered.iterrows():
    node = Node(
        id=row["pubmed_id"],
        label=make_label(row),
        size=15 if row["funding_source"] != "Fondazione Telethon" else 25,
        color=color_for_node(row)
    )
    nodes.append(node)

# Edges
for _, row in df_edges.iterrows():
    edge_color = "#F4A261" if highlight_ft and row["source"] == "FT2020-001" else "#CCCCCC"
    edges.append(Edge(source=row["source"], target=row["target"], color=edge_color))

# ============================================================
# GRAPH CONFIGURATION
# ============================================================
config = Config(
    width="100%",
    height=600,
    directed=True,
    physics=True,
    hierarchical=False,
    nodeHighlightBehavior=True,
    highlightColor="#F4A261",
    collapsible=True,
)

# ============================================================
# DISPLAY GRAPH
# ============================================================
st.subheader("📈 Citation Graph")
agraph(nodes=nodes, edges=edges, config=config)

# ============================================================
# EXPANDABLE TABLE VIEW
# ============================================================
if show_table:
    with st.expander("📄 View publication details shown in the graph"):
        display_cols = ["title", "authors", "year", "journal", "funding_source", "layer"]
        st.dataframe(df_filtered[display_cols])
