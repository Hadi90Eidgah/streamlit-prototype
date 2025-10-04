import streamlit as st
import pandas as pd
import json
from streamlit_agraph import agraph, Node, Edge, Config
from pyvis.network import Network   # <-- NEW for export
import tempfile, os

# ... (keep all your existing code up to agraph(nodes, edges, config=config)) ...

# ============================================================
# DISPLAY GRAPH
# ============================================================
st.subheader("📊 Hierarchical Citation Tree")
agraph(nodes=nodes, edges=edges, config=config)

# ============================================================
# DOWNLOAD HIGH-RES GRAPH
# ============================================================
st.markdown("### 📥 Download Graph as High-Resolution Image")

# --- Generate PyVis network (off-screen) ---
net = Network(
    height="800px", width="100%",
    directed=True, bgcolor="#ffffff"
)
net.barnes_hut()

# add nodes
for n in nodes:
    net.add_node(
        n.id, label=n.label, color=n.color,
        size=n.size, title=n.label
    )

# add edges
for e in edges:
    net.add_edge(e.source, e.target, color=e.color, width=e.width)

# use a temporary file to export PNG
with tempfile.TemporaryDirectory() as tmpdir:
    html_path = os.path.join(tmpdir, "graph.html")
    png_path = os.path.join(tmpdir, "graph.png")
    net.show(html_path)

    # pyvis uses selenium under the hood for .show(); we mimic a high-res render using iframe screenshot
    # For portability in Streamlit Cloud, we simply export HTML for download (lightweight fallback)
    with open(html_path, "rb") as f:
        graph_bytes = f.read()

    st.download_button(
        label="💾 Download interactive graph (HTML)",
        data=graph_bytes,
        file_name="givinostat_graph.html",
        mime="text/html"
    )

    # Optional: provide JSON export (for external tools)
    graph_json_bytes = json.dumps(graph_data, indent=2).encode("utf-8")
    st.download_button(
        label="📄 Download graph data (JSON)",
        data=graph_json_bytes,
        file_name="givinostat_graph.json",
        mime="application/json"
    )

# ============================================================
# EXPANDABLE TABLE VIEW
# ============================================================
if show_table:
    with st.expander("📄 View publication details shown in the graph"):
        display_cols = ["title", "authors", "year", "journal", "funding_source", "layer"]
        st.dataframe(df_filtered[display_cols])
