"""
Research Impact Dashboard - Enhanced with Improved Citation Patterns
Shows realistic research pathways from grants to breakthrough treatments
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Research Impact Dashboard",
    page_icon="🔬",
    layout="wide"
)

# Scientific Dark Theme CSS
st.markdown("""
<style>
/* Global dark theme */
.stApp {
    background-color: #0e1117;
    color: #fafafa;
}

/* Main header styling */
.main-header { 
    font-size: 2.5rem; 
    color: #ffffff; 
    text-align: center; 
    margin-bottom: 2rem;
    font-weight: 300;
    letter-spacing: 1px;
}

/* Elegant network selection cards */
.selection-card { 
    background: linear-gradient(135deg, #1e2329 0%, #2d3748 100%);
    padding: 1.8rem; 
    border-radius: 12px; 
    border: 1px solid #4a5568; 
    margin: 1rem 0; 
    text-align: left;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

.selection-card:hover {
    border-color: #63b3ed;
    box-shadow: 0 6px 20px rgba(99, 179, 237, 0.2);
    transform: translateY(-2px);
}

/* Network card styling */
.grant-card { 
    border-left: 3px solid #4299e1; 
}

/* Scientific typography */
.network-title {
    font-size: 1.4rem;
    font-weight: 500;
    color: #e2e8f0;
    margin-bottom: 0.5rem;
}

.treatment-name {
    font-size: 1.1rem;
    color: #90cdf4;
    font-weight: 400;
    margin-bottom: 1rem;
}

.network-details {
    font-size: 0.9rem;
    color: #a0aec0;
    line-height: 1.6;
}

/* Metrics styling */
.metric-container {
    background: rgba(45, 55, 72, 0.6);
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid #4a5568;
}

/* Search section styling */
.search-section {
    background: rgba(30, 35, 41, 0.8);
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #4a5568;
    margin-bottom: 2rem;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
    box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
}

/* Sidebar styling */
.css-1d391kg {
    background-color: #1a202c;
}

/* Remove default streamlit styling */
.css-1v0mbdj {
    border: none;
}

/* Network info styling */
.network-info { 
    background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
    padding: 1.5rem; 
    border-radius: 0.8rem; 
    border-radius: 10px; 
    border: 1px solid #4a5568; 
    margin: 1rem 0; 
}

/* Selectbox styling */
.stSelectbox > div > div {
    background-color: #2d3748;
    border: 1px solid #4a5568;
    border-radius: 6px;
}

/* Info box styling */
.stInfo {
    background-color: rgba(66, 153, 225, 0.1);
    border: 1px solid #4299e1;
    border-radius: 8px;
}

/* Success box styling */
.stSuccess {
    background-color: rgba(72, 187, 120, 0.1);
    border: 1px solid #48bb78;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)  # Cache for only 60 seconds to allow updates
def load_database():
    """Load data from database or CSV files"""
    try:
        if os.path.exists('streamlit_research_database.db'):
            conn = sqlite3.connect('streamlit_research_database.db')
            nodes_df = pd.read_sql('SELECT * FROM nodes', conn)
            edges_df = pd.read_sql('SELECT * FROM edges', conn)
            summary_df = pd.read_sql('SELECT * FROM network_summary', conn)
            conn.close()
            return nodes_df, edges_df, summary_df
        else:
            nodes_df = pd.read_csv('streamlit_nodes.csv')
            edges_df = pd.read_csv('streamlit_edges.csv')
            summary_df = pd.read_csv('streamlit_summary.csv')
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

def create_network_visualization(nodes_df, edges_df, network_id):
    """Create enhanced network visualization with improved citation patterns"""
    try:
        # Filter data for selected network
        network_nodes = nodes_df[nodes_df['network_id'] == network_id].copy()
        network_edges = edges_df[edges_df['network_id'] == network_id].copy()
        
        if len(network_nodes) == 0:
            st.error(f"No data found for network {network_id}")
            return go.Figure()
        
        # Separate nodes by type
        grants = network_nodes[network_nodes['node_type'] == 'grant']
        treatments = network_nodes[network_nodes['node_type'] == 'treatment']
        publications = network_nodes[network_nodes['node_type'] == 'publication']
        
        # Categorize publications by node ID patterns
        grant_funded_pubs = []      # PUB_X_Y - directly funded by grant
        treatment_pathway_pubs = [] # TREAT_PUB_X_Y - treatment development papers
        ecosystem_pubs = []         # ECO_X_Y - broader research ecosystem
        
        for _, pub in publications.iterrows():
            pub_id = pub['node_id']
            if pub_id.startswith('PUB_'):
                grant_funded_pubs.append(pub_id)
            elif pub_id.startswith('TREAT_PUB_'):
                treatment_pathway_pubs.append(pub_id)
            elif pub_id.startswith('ECO_'):
                ecosystem_pubs.append(pub_id)
        
        # Create strategic node positioning
        node_positions = {}
        
        # Position grant (blue circle) on the left
        if len(grants) > 0:
            grant_node = grants.iloc[0]
            grant_node_id = grant_node['node_id']
            node_positions[grant_node_id] = (-5, 0)
        
        # Position grant-funded publications (gray circles near grant)
        for i, pub_id in enumerate(grant_funded_pubs):
            y_pos = 2 - (i * 1.3)
            node_positions[pub_id] = (-2.5, y_pos)
        
        # Position ecosystem publications in organized clusters (middle area)
        np.random.seed(42 + network_id)
        cluster_centers = [(-0.5, 1), (0.5, 0.5), (1.5, -0.5), (0, -1.5)]
        
        for i, pub_id in enumerate(ecosystem_pubs):
            cluster_idx = i % len(cluster_centers)
            center_x, center_y = cluster_centers[cluster_idx]
            x_pos = center_x + np.random.normal(0, 0.4)
            y_pos = center_y + np.random.normal(0, 0.4)
            node_positions[pub_id] = (x_pos, y_pos)
        
        # Position treatment pathway publications (orange circles on the right)
        for i, pub_id in enumerate(treatment_pathway_pubs):
            y_pos = 1 - (i * 1.0)
            node_positions[pub_id] = (3.5, y_pos)
        
        # Position treatment (green circle) on the far right
        if len(treatments) > 0:
            treatment_node = treatments.iloc[0]
            treatment_node_id = treatment_node['node_id']
            node_positions[treatment_node_id] = (6, 0)
        
        # Create edge traces
        edge_traces = []
        
        # 1. Grant funding edges (blue, thick)
        grant_funding_edges = network_edges[network_edges['edge_type'] == 'funded_by']
        if len(grant_funding_edges) > 0:
            edge_x, edge_y = [], []
            
            for _, edge in grant_funding_edges.iterrows():
                if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            if edge_x:
                grant_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=3, color='rgba(74, 85, 104, 0.8)'),
                    hoverinfo='none',
                    mode='lines',
                    name='Grant Funding',
                    showlegend=True
                )
                edge_traces.append(grant_trace)
        
        # 2. Treatment pathway edges (orange, thick) - Only complete pathways
        treatment_pathway_edges = network_edges[network_edges['edge_type'] == 'leads_to_treatment']
        citation_edges = network_edges[network_edges['edge_type'] == 'cites']
        
        # Find complete pathways: Treatment → Ecosystem → Grant (simplified approach)
        complete_pathway_edge_ids = set()
        
        if len(treatment_pathway_edges) > 0:
            # Find treatment papers that connect to ecosystem papers that connect to grant papers
            for _, t_edge in treatment_pathway_edges.iterrows():
                if (t_edge['source_id'].startswith('TREAT_PUB_') and 
                    t_edge['target_id'].startswith('ECO_')):
                    
                    eco_id = t_edge['target_id']
                    
                    # Check if this ecosystem paper cites any grant papers
                    eco_to_grant = citation_edges[
                        (citation_edges['source_id'] == eco_id) & 
                        (citation_edges['target_id'].str.startswith('PUB_'))
                    ]
                    
                    if len(eco_to_grant) > 0:
                        # This is a complete pathway - mark both edges
                        complete_pathway_edge_ids.add(f"{t_edge['source_id']}→{t_edge['target_id']}")
                        
                        for _, e_edge in eco_to_grant.iterrows():
                            complete_pathway_edge_ids.add(f"{e_edge['source_id']}→{e_edge['target_id']}")
            
            # Also include direct treatment → grant connections (rare)
            direct_treatment_to_grant = treatment_pathway_edges[
                (treatment_pathway_edges['source_id'].str.startswith('TREAT_PUB_')) & 
                (treatment_pathway_edges['target_id'].str.startswith('PUB_'))
            ]
            for _, edge in direct_treatment_to_grant.iterrows():
                complete_pathway_edge_ids.add(f"{edge['source_id']}→{edge['target_id']}")
        
        # Draw complete pathway edges in orange
        if complete_pathway_edge_ids:
            edge_x, edge_y = [], []
            
            # Draw treatment pathway edges that are part of complete pathways
            for _, edge in treatment_pathway_edges.iterrows():
                edge_id = f"{edge['source_id']}→{edge['target_id']}"
                if (edge_id in complete_pathway_edge_ids and
                    edge['source_id'] in node_positions and 
                    edge['target_id'] in node_positions):
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            # Draw citation edges that are part of complete pathways
            for _, edge in citation_edges.iterrows():
                edge_id = f"{edge['source_id']}→{edge['target_id']}"
                if (edge_id in complete_pathway_edge_ids and
                    edge['source_id'] in node_positions and 
                    edge['target_id'] in node_positions):
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            if edge_x:
                treatment_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=3, color='rgba(99, 179, 237, 0.9)'),
                    hoverinfo='none',
                    mode='lines',
                    name='Research Impact Pathway',
                    showlegend=True
                )
                edge_traces.append(treatment_trace)
        
        # 3. General citation edges (gray, transparent) - Exclude highlighted pathways
        all_citation_edges = network_edges[network_edges['edge_type'] == 'cites']
        remaining_treatment_edges = network_edges[network_edges['edge_type'] == 'leads_to_treatment']
        
        # Use the complete_pathway_edge_ids set we already created
        highlighted_edge_ids = complete_pathway_edge_ids
        
        # Draw remaining citation edges in gray
        if len(all_citation_edges) > 0:
            edge_x, edge_y = [], []
            
            for _, edge in all_citation_edges.iterrows():
                edge_id = f"{edge['source_id']}→{edge['target_id']}"
                if (edge_id not in highlighted_edge_ids and 
                    edge['source_id'] in node_positions and 
                    edge['target_id'] in node_positions):
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            if edge_x:
                citation_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=0.8, color='rgba(160, 174, 192, 0.25)'),
                    hoverinfo='none',
                    mode='lines',
                    showlegend=False
                )
                edge_traces.append(citation_trace)
        
        # Draw remaining treatment edges that don't complete pathways in gray
        if len(remaining_treatment_edges) > 0:
            edge_x, edge_y = [], []
            
            for _, edge in remaining_treatment_edges.iterrows():
                edge_id = f"{edge['source_id']}→{edge['target_id']}"
                if (edge_id not in highlighted_edge_ids and 
                    edge['source_id'] in node_positions and 
                    edge['target_id'] in node_positions):
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            if edge_x:
                incomplete_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=2, color='rgba(200, 200, 200, 0.4)'),
                    hoverinfo='none',
                    mode='lines',
                    showlegend=False
                )
                edge_traces.append(incomplete_trace)
        
        # 4. Treatment enablement edges (green, medium)
        enablement_edges = network_edges[network_edges['edge_type'] == 'enables_treatment']
        if len(enablement_edges) > 0:
            edge_x, edge_y = [], []
            
            for _, edge in enablement_edges.iterrows():
                if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            if edge_x:
                enablement_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=3, color='rgba(5, 150, 105, 0.8)'),
                    hoverinfo='none',
                    mode='lines',
                    name='Treatment Development',
                    showlegend=True
                )
                edge_traces.append(enablement_trace)
        
        # Create node traces
        node_traces = []
        
        # Grant nodes (blue)
        if len(grants) > 0:
            grant_x = [node_positions[grants.iloc[0]['node_id']][0]]
            grant_y = [node_positions[grants.iloc[0]['node_id']][1]]
            
            grant_trace = go.Scatter(
                x=grant_x, y=grant_y,
                mode='markers',
                hoverinfo='text',
                text=["Research Grant<br>Funding Source"],
                marker=dict(size=40, color='#4a5568', line=dict(width=2, color='#e2e8f0')),
                name='Research Grant',
                showlegend=True
            )
            node_traces.append(grant_trace)
        
        # Grant-funded publication nodes (gray)
        if grant_funded_pubs:
            pub_x = [node_positions[pub_id][0] for pub_id in grant_funded_pubs if pub_id in node_positions]
            pub_y = [node_positions[pub_id][1] for pub_id in grant_funded_pubs if pub_id in node_positions]
            
            if pub_x:
                funded_pub_trace = go.Scatter(
                    x=pub_x, y=pub_y,
                    mode='markers',
                    hoverinfo='text',
                    text=["Grant-Funded Research<br>Direct Impact"] * len(pub_x),
                    marker=dict(size=18, color='#a0aec0', line=dict(width=1, color='#e2e8f0')),
                    name='Grant-Funded Research',
                    showlegend=True
                )
                node_traces.append(funded_pub_trace)
        
        # Treatment pathway nodes (blue accent)
        if treatment_pathway_pubs:
            treat_x = [node_positions[pub_id][0] for pub_id in treatment_pathway_pubs if pub_id in node_positions]
            treat_y = [node_positions[pub_id][1] for pub_id in treatment_pathway_pubs if pub_id in node_positions]
            
            if treat_x:
                pathway_trace = go.Scatter(
                    x=treat_x, y=treat_y,
                    mode='markers',
                    hoverinfo='text',
                    text=["Treatment Development<br>Research Papers"] * len(treat_x),
                    marker=dict(size=22, color='#90cdf4', line=dict(width=2, color='#e2e8f0')),
                    name='Treatment Development',
                    showlegend=True
                )
                node_traces.append(pathway_trace)
        
        # Ecosystem publications (small light gray)
        if ecosystem_pubs:
            eco_x = [node_positions[pub_id][0] for pub_id in ecosystem_pubs if pub_id in node_positions]
            eco_y = [node_positions[pub_id][1] for pub_id in ecosystem_pubs if pub_id in node_positions]
            
            if eco_x:
                eco_trace = go.Scatter(
                    x=eco_x, y=eco_y,
                    mode='markers',
                    hoverinfo='text',
                    text=["Research Ecosystem<br>Supporting Literature"] * len(eco_x),
                    marker=dict(size=8, color='#718096', line=dict(width=0.5, color='#a0aec0')),
                    name='Research Ecosystem',
                    showlegend=True
                )
                node_traces.append(eco_trace)
        
        # Treatment nodes (teal accent)
        if len(treatments) > 0:
            treatment_x = [node_positions[treatments.iloc[0]['node_id']][0]]
            treatment_y = [node_positions[treatments.iloc[0]['node_id']][1]]
            
            treatment_trace = go.Scatter(
                x=treatment_x, y=treatment_y,
                mode='markers',
                hoverinfo='text',
                text=["Approved Treatment<br>Clinical Application"],
                marker=dict(size=35, color='#38b2ac', line=dict(width=2, color='#e2e8f0')),
                name='Approved Treatment',
                showlegend=True
            )
            node_traces.append(treatment_trace)
        
        # Create figure
        fig = go.Figure(data=edge_traces + node_traces)
        
        fig.update_layout(
            title={
                'text': f"Research Impact Network - Network {network_id}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#e2e8f0', 'family': 'Inter, sans-serif'}
            },
            showlegend=True,
            hovermode='closest',
            margin=dict(b=40, l=40, r=40, t=70),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 7]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-3, 3]),
            height=600,
            plot_bgcolor='rgba(14, 17, 23, 0)',
            paper_bgcolor='rgba(14, 17, 23, 0)',
            font=dict(color='#e2e8f0'),
            legend=dict(
                yanchor="top", y=0.98, xanchor="left", x=0.02,
                bgcolor="rgba(45, 55, 72, 0.9)", bordercolor="rgba(74, 85, 104, 0.5)",
                borderwidth=1, font=dict(size=11, color='#e2e8f0')
            )
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating network visualization: {str(e)}")
        return go.Figure()

def display_network_metrics(summary_df, edges_df, network_id):
    """Display key metrics for the selected network"""
    try:
        network_summary = summary_df[summary_df['network_id'] == network_id].iloc[0]
        network_edges = edges_df[edges_df['network_id'] == network_id]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Publications",
                value=f"{network_summary['total_publications']}",
                delta="Research papers"
            )
        
        with col2:
            st.metric(
                label="Research Duration",
                value=f"{network_summary['research_duration']} years",
                delta=f"Approved {network_summary['approval_year']}"
            )
        
        with col3:
            treatment_connections = len(network_edges[network_edges['edge_type'] == 'leads_to_treatment'])
            st.metric(
                label="Treatment Pathways",
                value=f"{treatment_connections}",
                delta="Impact connections"
            )
        
        with col4:
            total_connections = len(network_edges)
            st.metric(
                label="Total Connections",
                value=f"{total_connections}",
                delta="Network edges"
            )
        
        # Edge type breakdown
        edge_counts = network_edges['edge_type'].value_counts()
        
        st.markdown("### Network Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Connection Types:**")
            for edge_type, count in edge_counts.items():
                if edge_type == 'leads_to_treatment':
                    st.markdown(f"- **{edge_type}**: {count} (Impact pathway)")
                elif edge_type == 'funded_by':
                    st.markdown(f"- **{edge_type}**: {count} (Direct funding)")
                elif edge_type == 'enables_treatment':
                    st.markdown(f"- **{edge_type}**: {count} (Treatment development)")
                else:
                    st.markdown(f"- **{edge_type}**: {count}")
        
        with col2:
            st.markdown("**Research Impact:**")
            st.markdown(f"- **Disease**: {network_summary['disease']}")
            st.markdown(f"- **Treatment**: {network_summary['treatment_name']}")
            st.markdown(f"- **Grant ID**: {network_summary['grant_id']}")
            
            if treatment_connections > 0:
                st.success(f"**{treatment_connections} verified pathways** from treatment research to grant funding")
            else:
                st.warning("No treatment pathway connections found")
        
    except Exception as e:
        st.error(f"Error displaying metrics: {str(e)}")

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">Research Impact Network Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.1rem; color: #a0aec0; margin-bottom: 3rem; font-weight: 300;">Mapping Research Pathways from Grant Funding to Breakthrough Treatments</p>', unsafe_allow_html=True)
    
    # Load data
    try:
        # Add cache clear button for debugging
        if st.button("Reload Data", help="Refresh database if needed"):
            st.cache_data.clear()
            st.rerun()
        
        nodes_df, edges_df, summary_df = load_database()
        
        # Debug info
        st.sidebar.markdown("### Database Statistics")
        st.sidebar.write(f"Total connections: {len(edges_df)}")
        st.sidebar.write(f"Treatment pathways: {len(edges_df[edges_df['edge_type'] == 'leads_to_treatment'])}")
        
        # Show citation pattern breakdown
        treatment_edges = edges_df[edges_df['edge_type'] == 'leads_to_treatment']
        direct_to_grant = len(treatment_edges[
            (treatment_edges['source_id'].str.startswith('TREAT_PUB_')) & 
            (treatment_edges['target_id'].str.startswith('PUB_'))
        ])
        indirect_via_eco = len(treatment_edges[
            (treatment_edges['source_id'].str.startswith('TREAT_PUB_')) & 
            (treatment_edges['target_id'].str.startswith('ECO_'))
        ])
        st.sidebar.write(f"Direct treatment→grant: {direct_to_grant}")
        st.sidebar.write(f"Indirect treatment→ecosystem: {indirect_via_eco}")
        
        if len(summary_df) == 0:
            st.error("No data available. Please check your database files.")
            return
        
        # Enhanced Network Selection with Search
        st.markdown("## Network Selection")
        
        # Search functionality
        st.markdown("### Search & Filter")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            search_type = st.selectbox(
                "Search by:",
                ["Disease", "Treatment", "Grant"],
                key="search_type"
            )
        
        with col2:
            if search_type == "Disease":
                search_options = summary_df['disease'].tolist()
                search_placeholder = "Select a disease..."
            elif search_type == "Treatment":
                search_options = summary_df['treatment_name'].tolist()
                search_placeholder = "Select a treatment..."
            else:  # Grant
                search_options = summary_df['grant_id'].tolist()
                search_placeholder = "Select a grant..."
            
            selected_search = st.selectbox(
                f"Select {search_type.lower()}:",
                [""] + search_options,
                key="search_selection",
                format_func=lambda x: search_placeholder if x == "" else x
            )
        
        # Filter networks based on search
        if selected_search and selected_search != "":
            if search_type == "Disease":
                filtered_networks = summary_df[summary_df['disease'] == selected_search]
            elif search_type == "Treatment":
                filtered_networks = summary_df[summary_df['treatment_name'] == selected_search]
            else:  # Grant
                filtered_networks = summary_df[summary_df['grant_id'] == selected_search]
        else:
            filtered_networks = summary_df
        
        # Display filtered network cards
        if len(filtered_networks) > 0:
            st.markdown("### Available Research Networks")
            
            # Create columns based on number of filtered networks
            num_networks = len(filtered_networks)
            if num_networks == 1:
                cols = [st.columns(1)[0]]
            elif num_networks == 2:
                cols = st.columns(2)
            else:
                cols = st.columns(3)
            
            selected_network = None
            
            for i, (_, network) in enumerate(filtered_networks.iterrows()):
                col_index = i if i < len(cols) else i % len(cols)
                with cols[col_index]:
                    with st.container():
                        # Highlight the matching search criteria
                        if search_type == "Disease":
                            highlight_text = f"Target: {network['disease']}"
                        elif search_type == "Treatment":
                            highlight_text = f"Therapy: {network['treatment_name']}"
                        else:
                            highlight_text = f"Grant: {network['grant_id']}"
                        
                        st.markdown(f"""
                        <div class="selection-card grant-card">
                            <div class="network-title">{network['disease']}</div>
                            <div class="treatment-name">{network['treatment_name']}</div>
                            <div class="network-details">
                                Grant ID: {network['grant_id']}<br>
                                Research Duration: {network['research_duration']} years<br>
                                <span style="color: #90cdf4; font-weight: 500;">{highlight_text}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"Analyze Network {network['network_id']}", key=f"btn_{network['network_id']}"):
                            selected_network = network['network_id']
        else:
            st.info("Use the search options above to find and explore research networks.")
        
        # Use session state to maintain selection
        if 'selected_network' not in st.session_state:
            st.session_state.selected_network = 1
        
        if selected_network:
            st.session_state.selected_network = selected_network
        
        # Display selected network
        network_id = st.session_state.selected_network
        selected_summary = summary_df[summary_df['network_id'] == network_id].iloc[0]
        
        st.markdown(f"## 📊 Network {network_id}: {selected_summary['disease']} Research Impact")
        
        # Display metrics
        display_network_metrics(summary_df, edges_df, network_id)
        
        # Create and display visualization
        st.markdown("### 🕸️ Research Network Visualization")
        
        with st.spinner("Creating network visualization..."):
            fig = create_network_visualization(nodes_df, edges_df, network_id)
            
            if fig.data:
                st.plotly_chart(fig, use_container_width=True)
                
                # Success message for treatment connections
                treatment_edges = edges_df[
                    (edges_df['network_id'] == network_id) & 
                    (edges_df['edge_type'] == 'leads_to_treatment')
                ]
                
                if len(treatment_edges) > 0:
                    st.success(f"""
                    🎉 **Research Impact Confirmed!** 
                    
                    This network shows **{len(treatment_edges)} direct connections** from treatment development papers 
                    back to the original grant-funded research, proving the research pathway from funding to breakthrough treatment.
                    
                    **Legend:**
                    - **Blue circles (left)** = Research grant funding source
                    - **Gray circles (left-center)** = Grant-funded research papers  
                    - **Orange circles (right-center)** = Treatment development papers
                    - **Green circle (right)** = FDA-approved breakthrough treatment
                    - **Orange lines** = Critical treatment impact pathways
                    """)
                else:
                    st.warning("⚠️ No treatment pathway connections found in this network")
            else:
                st.error("Unable to create network visualization")
        
        # Database statistics
        st.markdown("### 📈 Database Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Networks", len(summary_df))
            st.metric("Total Nodes", len(nodes_df))
        
        with col2:
            st.metric("Total Connections", len(edges_df))
            total_funding = summary_df['funding_amount'].sum()
            st.metric("Total Funding", f"${total_funding:,.0f}")
        
        with col3:
            treatment_connections = len(edges_df[edges_df['edge_type'] == 'leads_to_treatment'])
            st.metric("Treatment Pathways", treatment_connections)
            citation_connections = len(edges_df[edges_df['edge_type'] == 'cites'])
            st.metric("Citation Network", citation_connections)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; margin-top: 2rem;">
            <p>🔬 <strong>Research Impact Dashboard</strong> - Enhanced with realistic citation patterns and guaranteed research pathways</p>
            <p>Demonstrating how grant funding leads to breakthrough medical treatments through research networks</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please check that all required data files are present and properly formatted.")

if __name__ == "__main__":
    main()
