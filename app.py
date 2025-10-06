import streamlit as st
import pandas as pd
import sqlite3
import os
import numpy as np
from config import *
from pyvis.network import Network
import tempfile
import streamlit.components.v1 as components

# --- Page Configuration ---
st.set_page_config(
    page_title="Research Impact Dashboard",
    page_icon="🔬",
    layout="wide"
)

# --- Load External CSS ---
def load_css(file_name):
    """Load CSS and re-inject after render to override Streamlit theming."""
    import time
    with open(file_name) as f:
        css = f.read()

    # Inject CSS initially
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # Re-inject CSS after render (helps override Streamlit Cloud theme)
    st.markdown(
        f"""
        <script>
            setTimeout(function() {{
                var css = `{css}`;
                var style = document.createElement('style');
                style.innerHTML = css;
                document.head.appendChild(style);
                console.log('✅ Forced CSS reinjection {int(time.time())}');
            }}, 1500);
        </script>
        """,
        unsafe_allow_html=True
    )

load_css('style.css')

# --- Data Loading ---
@st.cache_data(ttl=CACHE_TTL)
def load_database():
    """Load data from database or CSV files"""
    try:
        if os.path.exists(DATABASE_PATH):
            conn = sqlite3.connect(DATABASE_PATH)
            nodes_df = pd.read_sql('SELECT * FROM nodes', conn)
            edges_df = pd.read_sql('SELECT * FROM edges', conn)
            summary_df = pd.read_sql('SELECT * FROM network_summary', conn)
            conn.close()
            return nodes_df, edges_df, summary_df
        else:
            nodes_df = pd.read_csv(NODES_CSV_PATH)
            edges_df = pd.read_csv(EDGES_CSV_PATH)
            summary_df = pd.read_csv(SUMMARY_CSV_PATH)
            return nodes_df, edges_df, summary_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create fallback sample data"""
    summary_df = pd.DataFrame({
        'network_id': [1, 2, 3],
        'disease': ['Cancer', 'Alzheimer Disease', 'Diabetes'],
        'treatment_name': ['CAR-T Cell Therapy', 'Aducanumab Plus', 'Smart Insulin Patch'],
        'grant_id': ['INST-R01-877572', 'INST-U01-352422', 'INST-U01-448787'],
        'grant_year': [2015, 2019, 2015],
        'approval_year': [2024, 2023, 2025],
        'funding_amount': [2807113, 2304762, 1983309],
        'total_publications': [37, 37, 37],
        'research_duration': [9, 4, 10]
    })
    
    nodes_df = pd.DataFrame({
        'node_id': ['GRANT_1', 'GRANT_2', 'GRANT_3', 'TREAT_1', 'TREAT_2', 'TREAT_3'],
        'node_type': ['grant', 'grant', 'grant', 'treatment', 'treatment', 'treatment'],
        'network_id': [1, 2, 3, 1, 2, 3]
    })
    
    edges_df = pd.DataFrame({
        'source_id': ['GRANT_1', 'GRANT_2', 'GRANT_3'],
        'target_id': ['TREAT_1', 'TREAT_2', 'TREAT_3'],
        'edge_type': ['leads_to', 'leads_to', 'leads_to'],
        'network_id': [1, 2, 3]
    })
    
    return nodes_df, edges_df, summary_df

# --- UI Components ---
def display_network_metrics(summary_df, edges_df, network_id):
    """Display key metrics for the selected network"""
    try:
        network_summary = summary_df[summary_df['network_id'] == network_id].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(label="Publications", value=f"{network_summary['total_publications']}", delta="Research papers")
        with col2:
            st.metric(label="Research Duration", value=f"{network_summary['research_duration']} years", delta=f"Approved {network_summary['approval_year']}")

    except Exception as e:
        st.error(f"Error displaying metrics: {str(e)}")


# --- PyVis Visualization ---
def create_pyvis_network(nodes_df, edges_df, network_id):
    """Create an interactive PyVis network visualization."""
    net = Network(height="620px", width="100%", bgcolor="#0e1117", font_color="#e2e8f0")

    # Filter for the selected network
    network_nodes = nodes_df[nodes_df['network_id'] == network_id]
    network_edges = edges_df[edges_df['network_id'] == network_id]

    # Add nodes
    for _, node in network_nodes.iterrows():
        node_color = NODE_COLORS.get(node['node_type'], "#718096")
        node_size = NODE_SIZES.get(node['node_type'], 12)
        node_label = node.get("title", node['node_id'])
        tooltip = f"<b>{node['node_type'].capitalize()}</b><br>{node_label}"
        net.add_node(node['node_id'], label=node_label, color=node_color, title=tooltip, size=node_size)

    # Add edges
    for _, edge in network_edges.iterrows():
        edge_color = EDGE_COLORS.get(edge['edge_type'], "rgba(99, 179, 237, 0.8)")
        net.add_edge(edge['source_id'], edge['target_id'], color=edge_color)

    # Enable physics layout (organic look)
    net.barnes_hut(gravity=-30000, spring_length=200, spring_strength=0.02)

    # Save to temporary HTML and render in Streamlit
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        net.save_graph(tmp.name)
        html = open(tmp.name, "r", encoding="utf-8").read()

    components.html(html, height=640, scrolling=True)


# --- Main Application ---
def main():
    st.markdown('<h1 class="main-header">Research Impact Network Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.1rem; color: #a0aec0; margin-bottom: 3rem; font-weight: 300;">Mapping Research Pathways from Grant Funding to Breakthrough Treatments</p>', unsafe_allow_html=True)

    # Load data
    nodes_df, edges_df, summary_df = load_database()

    st.sidebar.markdown("### Database Statistics")
    st.sidebar.write(f"Total connections: {len(edges_df)}")
    st.sidebar.write(f"Treatment pathways: {len(edges_df[edges_df['edge_type'] == EDGE_TYPE_LEADS_TO_TREATMENT])}")

    if summary_df.empty:
        st.error("No data available. Please check your database files.")
        return

    st.markdown("## Select the Citation Network")
    
    # Compact search controls
    with st.container():
        st.markdown('<div class="search-controls">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            search_type = st.selectbox("Search by:", ["Disease", "Treatment", "Grant"], key="search_type")
        
        with col2:
            if search_type == "Disease":
                search_options = summary_df['disease'].unique().tolist()
                search_placeholder = "Select a disease..."
            elif search_type == "Treatment":
                search_options = summary_df['treatment_name'].unique().tolist()
                search_placeholder = "Select a treatment..."
            else:  # Grant
                search_options = summary_df['grant_id'].unique().tolist()
                search_placeholder = "Select a grant..."

            selected_search = st.selectbox(f"Select {search_type.lower()}:", [""] + search_options, key="search_selection", format_func=lambda x: search_placeholder if x == "" else x)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Handle network selection
    if selected_search and selected_search != "":
        if search_type == "Disease":
            filtered_networks = summary_df[summary_df['disease'] == selected_search]
        elif search_type == "Treatment":
            filtered_networks = summary_df[summary_df['treatment_name'] == selected_search]
        else:
            filtered_networks = summary_df[summary_df['grant_id'] == selected_search]

        if not filtered_networks.empty:
            st.markdown("### Available Research Networks")
            num_networks = len(filtered_networks)
            cols = st.columns(min(num_networks, 3))
            selected_network = None

            for i, (_, network) in enumerate(filtered_networks.iterrows()):
                with cols[i % len(cols)]:
                    with st.container():
                        st.markdown(f"""<div class="selection-card grant-card">
                            <div class="network-title">{network['disease']}</div>
                            <div class="treatment-name">{network['treatment_name']}</div>
                            <div class="network-details">Grant ID: {network['grant_id']}<br>Duration: {network['research_duration']} years</div>
                        </div>""", unsafe_allow_html=True)
                        if st.button(f"Analyze Citation Network", key=f"btn_{network['network_id']}", use_container_width=True):
                            selected_network = network['network_id']
        else:
            st.info("No networks found for the selected criteria.")
    else:
        st.info("👆 Please select a disease, treatment, or grant from the dropdown above to view available research networks.")
        selected_network = None

    if selected_network:
        st.session_state.selected_network = selected_network

    if 'selected_network' in st.session_state and st.session_state.selected_network:
        network_id = st.session_state.selected_network
        current_networks = summary_df[summary_df['network_id'] == network_id]
        if not current_networks.empty:
            selected_summary = current_networks.iloc[0]
            
            st.markdown(f"## Citation Network: {selected_summary['disease']} Research Impact")
            display_network_metrics(summary_df, edges_df, network_id)

            st.markdown("### 🕸️ Research Network Visualization")
            with st.spinner("Building interactive network..."):
                create_pyvis_network(nodes_df, edges_df, network_id)
        else:
            st.session_state.selected_network = None


if __name__ == "__main__":
    main()
