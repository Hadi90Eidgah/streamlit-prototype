"""
Research Impact Dashboard - Selection-First Layout (SYNTAX FIXED)
Users choose a grant or treatment, then see the citation network
Perfect for stakeholder presentations and fundraising demonstrations
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Research Impact Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .selection-card {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
        text-align: center;
    }
    .grant-card {
        border-left: 6px solid #007bff;
    }
    .treatment-card {
        border-left: 6px solid #28a745;
    }
    .metric-highlight {
        font-size: 1.5rem;
        font-weight: bold;
        color: #495057;
    }
    .success-metric {
        color: #28a745;
        font-weight: bold;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Data loading functions
@st.cache_data
def load_database():
    """Load data from files in repository root"""
    try:
        # Try SQLite first
        if os.path.exists('streamlit_research_database.db'):
            conn = sqlite3.connect('streamlit_research_database.db')
            nodes_df = pd.read_sql('SELECT * FROM nodes', conn)
            edges_df = pd.read_sql('SELECT * FROM edges', conn)
            summary_df = pd.read_sql('SELECT * FROM network_summary', conn)
            conn.close()
            return nodes_df, edges_df, summary_df
        else:
            # Try CSV files
            nodes_df = pd.read_csv('streamlit_nodes.csv')
            edges_df = pd.read_csv('streamlit_edges.csv')
            summary_df = pd.read_csv('streamlit_summary.csv')
            return nodes_df, edges_df, summary_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create sample data if files are not available"""
    summary_df = pd.DataFrame({
        'network_id': [1, 2, 3],
        'disease': ['Cancer', 'Alzheimer\'s Disease', 'Diabetes'],
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

def create_citation_network(nodes_df, edges_df, selected_network_id):
    """Create detailed citation network for selected network"""
    try:
        # Filter data for selected network
        network_nodes = nodes_df[nodes_df['network_id'] == selected_network_id].copy()
        network_edges = edges_df[edges_df['network_id'] == selected_network_id].copy()
        
        if len(network_nodes) == 0:
            st.warning("No network data available")
            return go.Figure()
        
        # Create NetworkX graph
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for _, node in network_nodes.iterrows():
            node_attrs = {
                'type': node['node_type'],
                'label': node.get('node_label', str(node['node_id']))
            }
            G.add_node(node['node_id'], **node_attrs)
        
        # Add edges
        for _, edge in network_edges.iterrows():
            if edge['source_id'] in G.nodes() and edge['target_id'] in G.nodes():
                G.add_edge(edge['source_id'], edge['target_id'], 
                          type=edge.get('edge_type', 'connection'))
        
        if len(G.nodes()) == 0:
            return go.Figure()
        
        # Create hierarchical layout
        pos = create_hierarchical_layout(G, network_nodes)
        
        # Create edge traces
        edge_traces = []
        edge_types = network_edges['edge_type'].unique() if 'edge_type' in network_edges.columns else ['connection']
        
        colors = {
            'funded_by': '#007bff',
            'cites': '#6c757d', 
            'leads_to_treatment': '#ffc107',
            'enables_treatment': '#28a745',
            'connection': '#6c757d'
        }
        
        for edge_type in edge_types:
            type_edges = network_edges[network_edges['edge_type'] == edge_type] if 'edge_type' in network_edges.columns else network_edges
            
            edge_x = []
            edge_y = []
            
            for _, edge in type_edges.iterrows():
                if edge['source_id'] in pos and edge['target_id'] in pos:
                    x0, y0 = pos[edge['source_id']]
                    x1, y1 = pos[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            if edge_x:
                edge_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=2, color=colors.get(edge_type, '#6c757d')),
                    hoverinfo='none',
                    mode='lines',
                    name=edge_type.replace('_', ' ').title(),
                    showlegend=True
                )
                edge_traces.append(edge_trace)
        
        # Create node traces by type
        node_traces = []
        node_colors = {
            'grant': '#007bff',
            'publication': '#17a2b8',
            'treatment': '#28a745'
        }
        
        node_sizes = {
            'grant': 25,
            'publication': 12,
            'treatment': 20
        }
        
        for node_type in ['grant', 'publication', 'treatment']:
            type_nodes = network_nodes[network_nodes['node_type'] == node_type]
            
            if len(type_nodes) > 0:
                node_x = []
                node_y = []
                node_text = []
                
                for _, node in type_nodes.iterrows():
                    if node['node_id'] in pos:
                        x, y = pos[node['node_id']]
                        node_x.append(x)
                        node_y.append(y)
                        
                        # Create hover text
                        if node_type == 'grant':
                            text = f"Grant: {node.get('grant_id', node['node_id'])}<br>"
                            text += f"Funding: ${node.get('funding_amount', 0):,.0f}<br>"
                            text += f"Year: {node.get('year', 'N/A')}"
                        elif node_type == 'treatment':
                            text = f"Treatment: {node.get('treatment_name', node['node_id'])}<br>"
                            text += f"Approval: {node.get('approval_year', 'N/A')}"
                        else:  # publication
                            text = f"Publication: {node.get('pmid', node['node_id'])}<br>"
                            text += f"Title: {str(node.get('title', 'N/A'))[:50]}...<br>"
                            text += f"Year: {node.get('year', 'N/A')}"
                        
                        node_text.append(text)
                
                if node_x:
                    node_trace = go.Scatter(
                        x=node_x, y=node_y,
                        mode='markers',
                        hoverinfo='text',
                        text=node_text,
                        marker=dict(
                            size=node_sizes[node_type],
                            color=node_colors[node_type],
                            line=dict(width=2, color='white')
                        ),
                        name=f"{node_type.title()}s",
                        showlegend=True
                    )
                    node_traces.append(node_trace)
        
        # Create figure
        fig = go.Figure(data=edge_traces + node_traces)
        
        fig.update_layout(
            title=f"Citation Network - {len(network_nodes)} nodes, {len(network_edges)} connections",
            titlefont_size=16,
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating citation network: {e}")
        return go.Figure()

def create_hierarchical_layout(G, nodes_df):
    """Create hierarchical layout for network visualization"""
    try:
        # Group nodes by type
        grants = nodes_df[nodes_df['node_type'] == 'grant']['node_id'].tolist()
        publications = nodes_df[nodes_df['node_type'] == 'publication']['node_id'].tolist()
        treatments = nodes_df[nodes_df['node_type'] == 'treatment']['node_id'].tolist()
        
        pos = {}
        
        # Position grants at the top
        for i, grant in enumerate(grants):
            pos[grant] = (i * 2, 3)
        
        # Position treatments at the bottom
        for i, treatment in enumerate(treatments):
            pos[treatment] = (i * 2, 0)
        
        # Position publications in the middle with some randomness
        np.random.seed(42)
        for i, pub in enumerate(publications):
            x = np.random.uniform(-1, len(grants) * 2 + 1)
            y = np.random.uniform(1, 2)
            pos[pub] = (x, y)
        
        return pos
    
    except Exception:
        # Fallback to spring layout
        return nx.spring_layout(G, k=3, iterations=50)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔬 Research Impact Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Choose a Grant or Treatment to Explore the Citation Network</p>', unsafe_allow_html=True)
    
    # Load data
    nodes_df, edges_df, summary_df = load_database()
    
    # MAIN SELECTION INTERFACE
    st.header("🎯 Select Research to Explore")
    
    # Create two columns for selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Select by Grant")
        
        grant_options = {}
        for _, row in summary_df.iterrows():
            grant_options[f"{row['grant_id']} - {row['disease']}"] = row['network_id']
        
        selected_grant = st.selectbox(
            "Choose a research grant:",
            options=list(grant_options.keys()),
            key="grant_selector"
        )
        
        if selected_grant:
            selected_network_from_grant = grant_options[selected_grant]
            grant_info = summary_df[summary_df['network_id'] == selected_network_from_grant].iloc[0]
            
            grant_card_html = f"""
            <div class="selection-card grant-card">
                <h4>📋 {grant_info['grant_id']}</h4>
                <p><strong>Disease Focus:</strong> {grant_info['disease']}</p>
                <p><strong>Funding:</strong> ${grant_info['funding_amount']:,.0f}</p>
                <p><strong>Year:</strong> {grant_info['grant_year']}</p>
                <p class="metric-highlight">Duration: {grant_info['research_duration']} years</p>
            </div>
            """
            st.markdown(grant_card_html, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎯 Select by Treatment")
        
        treatment_options = {}
        for _, row in summary_df.iterrows():
            treatment_options[f"{row['treatment_name']} - {row['disease']}"] = row['network_id']
        
        selected_treatment = st.selectbox(
            "Choose a breakthrough treatment:",
            options=list(treatment_options.keys()),
            key="treatment_selector"
        )
        
        if selected_treatment:
            selected_network_from_treatment = treatment_options[selected_treatment]
            treatment_info = summary_df[summary_df['network_id'] == selected_network_from_treatment].iloc[0]
            
            treatment_card_html = f"""
            <div class="selection-card treatment-card">
                <h4>🎯 {treatment_info['treatment_name']}</h4>
                <p><strong>Disease:</strong> {treatment_info['disease']}</p>
                <p><strong>Approved:</strong> {treatment_info['approval_year']}</p>
                <p><strong>Publications:</strong> {treatment_info['total_publications']}</p>
                <p class="metric-highlight success-metric">✅ FDA Approved</p>
            </div>
            """
            st.markdown(treatment_card_html, unsafe_allow_html=True)
    
    # Determine which network to show
    selected_network_id = None
    selection_source = None
    
    if 'grant_selector' in st.session_state and selected_grant:
        selected_network_id = grant_options[selected_grant]
        selection_source = "grant"
    elif 'treatment_selector' in st.session_state and selected_treatment:
        selected_network_id = treatment_options[selected_treatment]
        selection_source = "treatment"
    
    # Show citation network if selection is made
    if selected_network_id:
        st.markdown("---")
        
        # Get network info
        network_info = summary_df[summary_df['network_id'] == selected_network_id].iloc[0]
        
        # Network header
        st.header(f"🕸️ Citation Network: {network_info['disease']} Research")
        
        # Network stats
        network_nodes = nodes_df[nodes_df['network_id'] == selected_network_id]
        network_edges = edges_df[edges_df['network_id'] == selected_network_id]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Nodes", len(network_nodes))
        
        with col2:
            st.metric("Connections", len(network_edges))
        
        with col3:
            publications = len(network_nodes[network_nodes['node_type'] == 'publication']) if 'node_type' in network_nodes.columns else 0
            st.metric("Publications", publications)
        
        with col4:
            st.metric("Research Duration", f"{network_info['research_duration']} years")
        
        # Citation network visualization
        st.subheader("📊 Interactive Citation Network")
        
        citation_fig = create_citation_network(nodes_df, edges_df, selected_network_id)
        st.plotly_chart(citation_fig, width='stretch')
        
        # Network explanation
        st.info("""
        **How to read this network:**
        - 🔵 **Blue nodes** = Research grants providing funding
        - 🔷 **Teal nodes** = Research publications and papers  
        - 🟢 **Green nodes** = Breakthrough treatments
        - **Lines** show citations and funding relationships
        - **Hover** over nodes for detailed information
        """)
        
        # Research pathway summary
        st.subheader("📈 Research Impact Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            research_summary = f"""
            **🔬 Research Journey:**
            - **Grant:** {network_info['grant_id']} ({network_info['grant_year']})
            - **Funding:** ${network_info['funding_amount']:,.0f}
            - **Publications:** {network_info['tota
(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)
