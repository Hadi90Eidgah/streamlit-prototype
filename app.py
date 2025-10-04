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
    "Number of layers to display:",
    min_value=1, max_value=5, value=5
)

highlight_ft = st.sidebar.checkbox(
    "Highlight Fondazione Telethon-funded papers", value=True
)

show_table = st.sidebar.checkbox("Show table below graph", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("👋 *Drag, zoom, and hover nodes for details.*")

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    with open("mock_graph_tree.json", "r") as f:
        graph_data = json.load(f)
    df_nodes = pd.read_csv("mock_nodes_tree.csv")
    df_edges = pd.read_csv("mock_edges_tree.csv")
    return graph_data, df_nodes, df_edges

graph_data, df_nodes, df_edges = load_data()

# ============================================================
# FILTER BY SELECTED DEPTH
# ============================================================
df_filtered = df_nodes[df_nodes["layer"] <= max_layers].copy()
valid_ids = set(df_filtered["pubmed_id"].tolist())
df_edges = df_edges[df_edges["target"].isin(valid_ids)]

# ============================================================
# HEADER & METRICS
# ============================================================
st.title("🌳 Research Lineage Tree: Givinostat")
st.markdown(
    """
    Visualizing how **Fondazione Telethon-funded research** evolved through multiple
    scientific layers to the **FDA/EMA approval** of *Givinostat*.
    """
)

col1, col2, col3 = st.columns(3)
col1.metric("Total Nodes", len(df_filtered))
col2.metric("FT Funded", df_filtered["funding_source"].eq("Fondazione Telethon").sum())
col3.metric("Layers", max_layers)

st.markdown("---")

# ============================================================
# NODE & EDGE CREATION
# ============================================================
def node_color(row):
    """Color scheme by type / layer."""
    if row["pubmed_id"] == "GIVINOSTAT":
        return "#E63946"  # red - treatment
    elif row["funding_source"] == "Fondazione Telethon":
        return "#2A9D8F"  # green - FT-funded
    elif row["pubmed_id"] == "FT2020-001":
        return "#6D597A"  # purple - FT Grant
    elif row["layer"] == 1:
        return "#457B9D"  # blue - approval papers
    elif row["layer"] == 2:
        return "#A8DADC"  # teal - intermediate
    elif row["layer"] == 3:
        return "#BFD3C1"  # pale green
    else:
        return "#CCCCCC"  # default gray

def make_label(row):
    label = f"{row['title']}\nYear: {row['year']}"
    if pd.notna(row.get("funding_source")):
        label += f"\nFunding: {row['funding_source']}"
    return label

nodes, edges = [], []

# Create nodes
for _, row in df_filtered.iterrows():
    nodes.append(Node(
        id=row["pubmed_id"],
        label=make_label(row),
        size=20 if row["funding_source"] == "Fondazione Telethon" else 15,
        color=node_color(row)
    ))

# Create edges
for _, row in df_edges.iterrows():
    color = "#F4A261" if highlight_ft and row["source"] == "FT2020-001" else "#999999"
    edges.append(Edge(
        source=row["source"],
        target=row["target"],
        color=color,
        width=2
    ))

# ============================================================
# GRAPH CONFIGURATION (Hierarchical Layout)
# ============================================================
config = Config(
    width="100%",
    height=650,
    directed=True,
    physics=False,
    hierarchical=True,
    hierarchical_sort_method="directed",
    hierarchical_level_distance=180,
    hierarchical_node_spacing=90,
    nodeHighlightBehavior=True,
    highlightColor="#F4A261",
    collapsible=True,
    bgcolor="#FFFFFF"
)

# ============================================================
# DISPLAY GRAPH
# ============================================================
st.subheader("📊 Hierarchical Citation Tree")
agraph(nodes=nodes, edges=edges, config=config)

# ============================================================
# DOWNLOAD GRAPH DATA (STREAMLIT CLOUD SAFE)
# ============================================================
st.markdown("### 📥 Download Graph Data")

# --- JSON graph download ---
graph_json_bytes = json.dumps(graph_data, indent=2).encode("utf-8")
st.download_button(
    label="📄 Download full graph (JSON)",
    data=graph_json_bytes,
    file_name="givinostat_graph.json",
    mime="application/json"
)

# --- CSV downloads (nodes and edges) ---
st.download_button(
    label="📊 Download node list (CSV)",
    data=df_filtered.to_csv(index=False).encode("utf-8"),
    file_name="givinostat_nodes.csv",
    mime="text/csv"
)

st.download_button(
    label="🔗 Download edge list (CSV)",
    data=df_edges.to_csv(index=False).encode("utf-8"),
    file_name="givinostat_edges.csv",
    mime="text/csv"
)

st.info(
    "💡 Tip: Open the JSON file in visualization tools like **Gephi**, **Cytoscape**, "
    "or **GraphCommons** to export a high-resolution image for presentations."
)

# ============================================================
# EXPANDABLE TABLE VIEW
# ============================================================
if show_table:
    with st.expander("📄 View publication details shown in the graph"):
        display_cols = ["title", "authors", "year", "journal", "funding_source", "layer"]
        st.dataframe(df_filtered[display_cols])
