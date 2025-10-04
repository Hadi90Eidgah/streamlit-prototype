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

selected_treatment = st.sidebar.selectbox("Select Treatment:", ["Givinostat"])
max_layers = st.sidebar.slider("Number of layers to display:", 1, 5, 5)
highlight_ft = st.sidebar.checkbox("Highlight Fondazione Telethon-funded papers", True)
show_table = st.sidebar.checkbox("Show table below graph", False)
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
    "Visualizing how **Fondazione Telethon-funded research** evolved through multiple "
    "scientific layers to the **FDA/EMA approval** of *Givinostat*."
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
    if row["pubmed_id"] == "GIVINOSTAT":
        return "#E63946"
    elif row["funding_source"] == "Fondazione Telethon":
        return "#2A9D8F"
    elif row["pubmed_id"] == "FT2020-001":
        return "#6D597A"
    elif row["layer"] == 1:
        return "#457B9D"
    elif row["layer"] == 2:
        return "#A8DADC"
    elif row["layer"] == 3:
        return "#BFD3C1"
    else:
        return "#CCCCCC"

def make_label(row):
    label = f"{row['title']}\nYear: {row['year']}"
    if pd.notna(row.get("funding_source")):
        label += f"\nFunding: {row['funding_source']}"
    return label

nodes, edges = [], []

for _, row in df_filtered.iterrows():
    nodes.append(Node(
        id=row["pubmed_id"],
        label=make_label(row),
        size=20 if row["funding_source"] == "Fondazione Telethon" else 15,
        color=node_color(row)
    ))

for _, row in df_edges.iterrows():
    color = "#F4A261" if highlight_ft and row["source"] == "FT2020-001" else "#999999"
    edges.append(Edge(source=row["source"], target=row["target"], color=color, width=2))

# ============================================================
# GRAPH CONFIGURATION
# ============================================================
config = Config(
    width="100%", height=650, directed=True, physics=False,
    hierarchical=True, hierarchical_sort_method="directed",
    hierarchical_level_distance=180, hierarchical_node_spacing=90,
    nodeHighlightBehavior=True, highlightColor="#F4A261",
    collapsible=True, bgcolor="#FFFFFF"
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

export_format = st.selectbox("Select export format:", ["PNG", "PDF"])

if st.button("📤 Generate & Download Image"):
    # Build NetworkX graph
    G = nx.DiGraph()
    for _, r in df_edges.iterrows():
        G.add_edge(r["source"], r["target"])

    # Make sure we color exactly G.nodes order
    node_colors = []
    for n in G.nodes():
        row_match = df_nodes[df_nodes["pubmed_id"] == n]
        if row_match.empty:
            node_colors.append("#CCCCCC")
        else:
            node_colors.append(node_color(row_match.iloc[0]))

    # Compute layout safely
    try:
        pos = nx.multipartite_layout(
            G,
            subset_key=lambda n: df_nodes.loc[df_nodes["pubmed_id"] == n, "layer"].values[0]
        )
    except Exception:
        pos = nx.spring_layout(G, seed=42)

    # Draw
    fig, ax = plt.subplots(figsize=(12, 8))
    nx.draw(
        G, pos,
        with_labels=False, arrows=True,
        node_color=node_colors, node_size=500,
        edge_color="#AAAAAA", alpha=0.9, ax=ax
    )

    for node in ["FT2020-001", "GIVINOSTAT"]:
        if node in G.nodes:
            x, y = pos[node]
            label = "FT Grant" if node == "FT2020-001" else "Givinostat (Treatment)"
            ax.text(x, y + 0.05, label, fontsize=10, ha="center", color="black")

    ax.set_title("Research Lineage Tree — Givinostat", fontsize=14, pad=20)
    ax.axis("off")

    buf = BytesIO()
    if export_format == "PNG":
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        mime, fname = "image/png", "givinostat_graph.png"
    else:
        plt.savefig(buf, format="pdf", dpi=300, bbox_inches="tight")
        mime, fname = "application/pdf", "givinostat_graph.pdf"
    plt.close(fig)
    buf.seek(0)

    st.download_button(f"💾 Download {export_format} Image", data=buf, file_name=fname, mime=mime)

# ============================================================
# DOWNLOAD GRAPH DATA (STREAMLIT CLOUD SAFE)
# ============================================================
st.markdown("### 📥 Download Graph Data")

graph_json_bytes = json.dumps(graph_data, indent=2).encode("utf-8")
st.download_button("📄 Download full graph (JSON)", graph_json_bytes,
                   "givinostat_graph.json", "application/json")

st.download_button("📊 Download node list (CSV)",
                   df_filtered.to_csv(index=False).encode("utf-8"),
                   "givinostat_nodes.csv", "text/csv")

st.download_button("🔗 Download edge list (CSV)",
                   df_edges.to_csv(index=False).encode("utf-8"),
                   "givinostat_edges.csv", "text/csv")

st.info("💡 Tip: Open the JSON file in **Gephi**, **Cytoscape**, or **GraphCommons** "
        "to produce advanced, high-resolution visualizations.")

# ============================================================
# EXPANDABLE TABLE VIEW
# ============================================================
if show_table:
    with st.expander("📄 View publication details shown in the graph"):
        cols = ["title", "authors", "year", "journal", "funding_source", "layer"]
        st.dataframe(df_filtered[cols])
