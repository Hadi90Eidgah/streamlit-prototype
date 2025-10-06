# Research Impact Dashboard - Optimized

import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import numpy as np
import os
from config import *
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Research Impact Dashboard",
    page_icon="🔬",
    layout="wide"
)

# --- Load External CSS ---
def load_css(file_name):
    """Load CSS and re-inject after render to override Streamlit theming."""
    with open(file_name) as f:
        css = f.read()

    # Inject CSS once
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # Re-inject after render (ensures override on Streamlit Cloud)
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
    )   st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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

# --- Visualization Functions ---

def get_node_positions(network_nodes, network_id):
    """Calculate node positions based on node type."""
    node_positions = {}
    np.random.seed(42 + network_id)

    # Position grant
    grants = network_nodes[network_nodes['node_type'] == NODE_TYPE_GRANT]
    if not grants.empty:
        node_positions[grants.iloc[0]['node_id']] = (NODE_POSITIONS_X['grant'], NODE_POSITIONS_Y['grant'])

    # Position publications
    publications = network_nodes[network_nodes['node_type'] == NODE_TYPE_PUBLICATION]
    grant_funded_pubs = [p for p in publications['node_id'] if p.startswith('PUB_')]
    treatment_pathway_pubs = [p for p in publications['node_id'] if p.startswith('TREAT_PUB_')]
    ecosystem_pubs = [p for p in publications['node_id'] if p.startswith('ECO_')]

    for i, pub_id in enumerate(grant_funded_pubs):
        node_positions[pub_id] = (NODE_POSITIONS_X['grant_funded_pub'], NODE_POSITIONS_Y['grant_funded_pub'][i % len(NODE_POSITIONS_Y['grant_funded_pub'])])

    for i, pub_id in enumerate(treatment_pathway_pubs):
        node_positions[pub_id] = (NODE_POSITIONS_X['treatment_pathway_pub'], NODE_POSITIONS_Y['treatment_pathway_pub'][i % len(NODE_POSITIONS_Y['treatment_pathway_pub'])])

    for i, pub_id in enumerate(ecosystem_pubs):
        cluster_idx = i % len(NODE_POSITIONS_X['ecosystem_pub_cluster'])
        center_x = NODE_POSITIONS_X['ecosystem_pub_cluster'][cluster_idx]
        center_y = NODE_POSITIONS_Y['ecosystem_pub_cluster'][cluster_idx]
        node_positions[pub_id] = (center_x + np.random.normal(0, 0.4), center_y + np.random.normal(0, 0.4))

    # Position treatment
    treatments = network_nodes[network_nodes['node_type'] == NODE_TYPE_TREATMENT]
    if not treatments.empty:
        node_positions[treatments.iloc[0]['node_id']] = (NODE_POSITIONS_X['treatment'], NODE_POSITIONS_Y['treatment'])

    return node_positions

def create_edge_trace(edges, node_positions, edge_type, name, showlegend):
    """Create a Plotly scatter trace for edges."""
    edge_x, edge_y = [], []
    for _, edge in edges.iterrows():
        if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
            x0, y0 = node_positions[edge['source_id']]
            x1, y1 = node_positions[edge['target_id']]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
    
    if not edge_x:
        return None

    return go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=EDGE_WIDTHS[edge_type], color=EDGE_COLORS[edge_type]),
        hoverinfo='none',
        mode='lines',
        name=name,
        showlegend=showlegend
    )

def create_node_trace(nodes, node_positions, node_type, name, text_template, showlegend):
    """Create a Plotly scatter trace for nodes."""
    node_x = [node_positions[node['node_id']][0] for _, node in nodes.iterrows() if node['node_id'] in node_positions]
    node_y = [node_positions[node['node_id']][1] for _, node in nodes.iterrows() if node['node_id'] in node_positions]

    if not node_x:
        return None

    return go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=[text_template] * len(node_x),
        marker=dict(size=NODE_SIZES[node_type], color=NODE_COLORS[node_type], line=dict(width=2, color='#e2e8f0')),
        name=name,
        showlegend=showlegend
    )

def create_network_visualization(nodes_df, edges_df, network_id, grant_id=None, treatment_name=None):
    """Create the network visualization."""
    network_nodes = nodes_df[nodes_df['network_id'] == network_id]
    network_edges = edges_df[edges_df['network_id'] == network_id]

    if network_nodes.empty:
        st.error(f"No data found for network {network_id}")
        return go.Figure()

    # Get grant ID and treatment name from the network data if not provided
    if grant_id is None:
        grant_node = network_nodes[network_nodes['node_type'] == NODE_TYPE_GRANT]
        grant_id = grant_node.iloc[0]['node_id'] if not grant_node.empty else f"Network {network_id}"
    
    if treatment_name is None:
        treatment_node = network_nodes[network_nodes['node_type'] == NODE_TYPE_TREATMENT]
        treatment_name = treatment_node.iloc[0]['node_id'] if not treatment_node.empty else "Treatment"

    node_positions = get_node_positions(network_nodes, network_id)

    edge_traces = [
        create_edge_trace(network_edges[network_edges['edge_type'] == EDGE_TYPE_FUNDED_BY], node_positions, EDGE_TYPE_FUNDED_BY, 'Grant Funding', True),
        create_edge_trace(network_edges[network_edges['edge_type'] == EDGE_TYPE_LEADS_TO_TREATMENT], node_positions, EDGE_TYPE_LEADS_TO_TREATMENT, 'Research Impact Pathway', True),
        create_edge_trace(network_edges[network_edges['edge_type'] == EDGE_TYPE_CITES], node_positions, EDGE_TYPE_CITES, 'Citation', False),
        create_edge_trace(network_edges[network_edges['edge_type'] == EDGE_TYPE_ENABLES_TREATMENT], node_positions, EDGE_TYPE_ENABLES_TREATMENT, 'Treatment Enablement', True),
    ]

    node_traces = [
        create_node_trace(network_nodes[network_nodes['node_type'] == NODE_TYPE_GRANT], node_positions, NODE_TYPE_GRANT, 'Grant', 'Research Grant<br>Funding Source', True),
        create_node_trace(network_nodes[network_nodes['node_id'].str.startswith('PUB_')], node_positions, 'grant_funded_pub', 'Grant-Funded Papers', 'Grant-Funded Paper', True),
        create_node_trace(network_nodes[network_nodes['node_id'].str.startswith('TREAT_PUB_')], node_positions, 'treatment_pathway_pub', 'Treatment Pathway Papers', 'Treatment Development Paper', True),
        create_node_trace(network_nodes[network_nodes['node_id'].str.startswith('ECO_')], node_positions, 'ecosystem_pub', 'Research Ecosystem', 'Research Ecosystem<br>Supporting Literature', True),
        create_node_trace(network_nodes[network_nodes['node_type'] == NODE_TYPE_TREATMENT], node_positions, NODE_TYPE_TREATMENT, 'Approved Treatment', 'Approved Treatment<br>Clinical Application', True),
    ]

    fig = go.Figure(data=[t for t in edge_traces + node_traces if t is not None])

    fig.update_layout(
        title={'text': f"Research Impact Network - {grant_id} → {treatment_name}", 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': '#e2e8f0', 'family': 'Inter, sans-serif'}},
        showlegend=True,
        hovermode='closest',
        margin=dict(b=40, l=40, r=40, t=70),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 7]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-3, 3]),
        height=600,
        plot_bgcolor='rgba(14, 17, 23, 0)',
        paper_bgcolor='rgba(14, 17, 23, 0)',
        font=dict(color='#e2e8f0'),
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02, bgcolor="rgba(45, 55, 72, 0.9)", bordercolor="rgba(74, 85, 104, 0.5)", borderwidth=1, font=dict(size=11, color='#e2e8f0'))
    )

    return fig

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

def main():
    """Main application function"""
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

    # Only show networks if a search selection has been made
    if selected_search and selected_search != "":
        if search_type == "Disease":
            filtered_networks = summary_df[summary_df['disease'] == selected_search]
        elif search_type == "Treatment":
            filtered_networks = summary_df[summary_df['treatment_name'] == selected_search]
        else:  # Grant
            filtered_networks = summary_df[summary_df['grant_id'] == selected_search]

        if not filtered_networks.empty:
            st.markdown("### Available Research Networks")
            
            # Create a more compact grid layout
            num_networks = len(filtered_networks)
            if num_networks <= 3:
                cols = st.columns(num_networks)
            else:
                cols = st.columns(3)
            
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
        # Show instruction message when no selection is made
        st.info("👆 Please select a disease, treatment, or grant from the dropdown above to view available research networks.")
        selected_network = None

    # Handle network selection and visualization
    if selected_network:
        if 'selected_network' not in st.session_state:
            st.session_state.selected_network = selected_network
        else:
            st.session_state.selected_network = selected_network

    # Only show network analysis if a network has been selected
    if 'selected_network' in st.session_state and st.session_state.selected_network:
        network_id = st.session_state.selected_network
        
        # Verify the network still exists in the current filtered data
        if selected_search and selected_search != "":
            # Use filtered networks
            if search_type == "Disease":
                current_networks = summary_df[summary_df['disease'] == selected_search]
            elif search_type == "Treatment":
                current_networks = summary_df[summary_df['treatment_name'] == selected_search]
            else:  # Grant
                current_networks = summary_df[summary_df['grant_id'] == selected_search]
            
            if network_id in current_networks['network_id'].values:
                selected_summary = current_networks[current_networks['network_id'] == network_id].iloc[0]
                
                st.markdown(f"## Citation Network: {selected_summary['disease']} Research Impact")
                display_network_metrics(summary_df, edges_df, network_id)

                st.markdown("### 🕸️ Research Network Visualization")
                with st.spinner("Creating network visualization..."):
                    fig = create_network_visualization(nodes_df, edges_df, network_id, 
                                                     grant_id=selected_summary['grant_id'], 
                                                     treatment_name=selected_summary['treatment_name'])
                    if fig.data:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Unable to create network visualization")
            else:
                # Selected network is not in current filter, clear selection
                st.session_state.selected_network = None
        else:
            # No search selection made, don't show network analysis
            pass

if __name__ == "__main__":
    main()

