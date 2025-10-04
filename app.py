import streamlit as st
import pandas as pd
import json
from streamlit_agraph import agraph, Node, Edge, Config
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO

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
# 📸 EXPORT GRAPH AS HIGH-RES IMAGE (PDF / PNG)
# ============================================================
st.markdown("### 🖼️ Export Graph as High-Resolution Image")

export_format = st.selectbox(
    "Select export format:",
    ["PNG", "PDF"]
)

if st.button("📤 Generate & Download Image"):
    # Build graph with NetworkX
    G = nx.DiGraph()
    for _, row in df_edges.iterrows():
        G.add_edge(row["source"], row["target"])

    # Create color map
    color_map = []
    for _, row in df_filtered.iterrows():
        if row["pubmed_id"] == "GIVINOSTAT":
            color_map.append("#E63946")
        elif row["funding_source"] == "Fondazione Telethon":
            color_map.append("#2A9D8F")
        elif row["pubmed_id"] == "FT2020-001":
            color_map.append("#6D597A")
        elif row["layer"] == 1:
            color_map.append("#457B9D")
        elif row["layer"] == 2:
            color_map.append("#A8DADC")
        elif row["layer"] == 3:
            color_map.append("#BFD3C1")
        else:
            color_map.append("#CCCCCC")

    # Layout by hierarchical layer
    try:
        pos = nx.multipartite_layout(
            G, subset_key=lambda n: df_nodes.loc[df_nodes["pubmed_id"] == n, "layer"].values[0]
        )
    except Exception:
        pos = nx.spring_layout(G, seed=42)

    # Draw with matplotlib
    fig, ax = plt.subplots(figsize=(12, 8))
    nx.draw(
        G, pos,
        with_labels=False,
        arrows=True,
        node_color=color_map,
        node_size=500,
        edge_color="#AAAAAA",
        alpha=0.9,
        ax=ax
    )

    # Label key nodes
    for node in ["FT2020-001", "GIVINOSTAT"]:
        if node in G.nodes:
            x, y = pos[node]
            label = "FT Grant" if node == "FT2020-001" else "Givinostat (Treatment)"
            ax.text(x, y + 0.05, label, fontsize=10, ha="center", color="black")

    ax.set_title("Research Lineage Tree — Givinostat", fontsize=14, pad=20)
    ax.axis("off")

    # Save to chosen format
    buf = BytesIO()
    if export_format == "PNG":
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        mime_type = "image/png"
        file_name = "givinostat_graph.png"
    else:
        plt.savefig(buf, format="pdf", dpi=300, bbox_inches="tight")
        mime_type = "application/pdf"
        file_name = "givinostat_graph.pdf"

    plt.close(fig)
    buf.seek(0)

    st.download_button(
        label=f"💾 Download {export_format} Image",
        data=buf,
        file_name=file_name,
        mime=mime_type
    )

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
    "💡 Tip: Open the JSON file in tools like **Gephi**, **Cytoscape**, "
    "or **GraphCommons** to produce advanced visualizations."
)

# ============================================================
# EXPANDABLE TABLE VIEW
# ============================================================
if show_table:
    with st.expander("📄 View publication details shown in the graph"):
        display_cols = ["title", "authors", "year", "journal", "funding_source", "layer"]
        st.dataframe(df_filtered[display_cols])
