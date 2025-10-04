import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import json
from collections import defaultdict, deque

# Page configuration
st.set_page_config(
    page_title="Research Grant to Treatment Lineage",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .node-details {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the dataset"""
    try:
        nodes_df = pd.read_csv('nodes.csv')
        edges_df = pd.read_csv('edges.csv')
        return nodes_df, edges_df
    except FileNotFoundError:
        st.error("Dataset files not found. Please ensure 'nodes.csv' and 'edges.csv' are in the same directory as this app.")
        st.stop()

def parse_node_details(details_str):
    """Parse the JSON details string into a dictionary"""
    try:
        return json.loads(details_str)
    except:
        return {}

def classify_nodes(nodes_df, edges_df):
    """Classify nodes based on their relationship to FT grant"""
    # Create sets for different node categories
    ft_funded_papers = set()
    citing_ft_papers = set()
    approval_papers = set()
    treatment_nodes = set()
    
    # Find FT-funded papers
    for _, node in nodes_df.iterrows():
        details = parse_node_details(node['details'])
        if node['node_type'] == 'paper' and 'ft_grant' in details:
            ft_funded_papers.add(node['node_id'])
        elif node['node_type'] == 'treatment':
            treatment_nodes.add(node['node_id'])
    
    # Find approval papers (papers that lead to treatment)
    for _, edge in edges_df.iterrows():
        if edge['edge_type'] == 'led_to_approval':
            approval_papers.add(edge['source_id'])
    
    # Find papers that cite FT-funded papers
    for _, edge in edges_df.iterrows():
        if edge['edge_type'] == 'cites' and edge['target_id'] in ft_funded_papers:
            citing_ft_papers.add(edge['source_id'])
    
    return ft_funded_papers, citing_ft_papers, approval_papers, treatment_nodes

def get_node_color(node_id, node_type, ft_funded, citing_ft, approval, treatment, distance):
    """Determine node color based on classification and distance"""
    base_colors = {
        'grant': '#1f77b4',  # Blue
        'ft_paper': '#1f77b4',  # Blue
        'citing_paper': '#ff7f0e',  # Orange
        'approval_paper': '#2ca02c',  # Green
        'treatment': '#2ca02c',  # Green
        'other_paper': '#d3d3d3'  # Light grey
    }
    
    # Determine base color category
    if node_type == 'grant':
        color_key = 'grant'
    elif node_id in treatment:
        color_key = 'treatment'
    elif node_id in approval:
        color_key = 'approval_paper'
    elif node_id in ft_funded:
        color_key = 'ft_paper'
    elif node_id in citing_ft:
        color_key = 'citing_paper'
    else:
        color_key = 'other_paper'
    
    base_color = base_colors[color_key]
    
    # Adjust intensity based on distance (if applicable)
    if distance >= 0 and color_key in ['citing_paper', 'other_paper']:
        # Make nodes closer to approval more intense
        max_distance = 5  # Assume max distance for normalization
        intensity = 1 - (distance / max_distance) * 0.5  # 0.5 to 1.0 range
        intensity = max(0.5, min(1.0, intensity))
        
        # Convert hex to RGB and apply intensity
        hex_color = base_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        adjusted_rgb = tuple(int(c * intensity + 255 * (1 - intensity)) for c in rgb)
        return f'rgb({adjusted_rgb[0]}, {adjusted_rgb[1]}, {adjusted_rgb[2]})'
    
    return base_color

def create_network_graph(nodes_df, edges_df):
    """Create an interactive network graph using Plotly"""
    # Create NetworkX graph for layout
    G = nx.DiGraph()
    
    # Add nodes
    for _, node in nodes_df.iterrows():
        G.add_node(node['node_id'], **node.to_dict())
    
    # Add edges
    for _, edge in edges_df.iterrows():
        G.add_edge(edge['source_id'], edge['target_id'], **edge.to_dict())
    
    # Calculate layout
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Classify nodes
    ft_funded, citing_ft, approval, treatment = classify_nodes(nodes_df, edges_df)
    
    # Prepare node traces
    node_x = []
    node_y = []
    node_colors = []
    node_sizes = []
    node_text = []
    node_hover = []
    
    for node_id in G.nodes():
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)
        
        node_data = G.nodes[node_id]
        details = parse_node_details(node_data['details'])
        distance = details.get('node_distance_to_approval', -1)
        
        # Determine color
        color = get_node_color(node_id, node_data['node_type'], ft_funded, citing_ft, approval, treatment, distance)
        node_colors.append(color)
        
        # Determine size based on node type
        if node_data['node_type'] == 'grant':
            size = 25
        elif node_data['node_type'] == 'treatment':
            size = 30
        elif node_id in approval:
            size = 20
        else:
            size = 15
        node_sizes.append(size)
        
        # Node labels
        if node_data['node_type'] == 'grant':
            label = 'FT Grant'
        elif node_data['node_type'] == 'treatment':
            label = details.get('approval_agency', 'Treatment')
        else:
            label = node_id[:8] + '...'
        node_text.append(label)
        
        # Hover information
        hover_info = f"<b>{node_data['node_label']}</b><br>"
        hover_info += f"Type: {node_data['node_type']}<br>"
        if 'title' in details:
            hover_info += f"Title: {details['title'][:50]}...<br>"
        if 'authors' in details:
            hover_info += f"Authors: {details['authors']}<br>"
        if 'year' in details:
            hover_info += f"Year: {details['year']}<br>"
        if distance >= 0:
            hover_info += f"Distance to Approval: {distance}<br>"
        node_hover.append(hover_info)
    
    # Prepare edge traces
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="middle center",
        textfont=dict(size=10, color='white'),
        hovertext=node_hover,
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white')
        )
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Research Grant to Treatment Lineage',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="Click on nodes to see details. Hover for quick information.",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002,
                            xanchor='left', yanchor='bottom',
                            font=dict(color='#888', size=12)
                        )],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        plot_bgcolor='white'
                    ))
    
    return fig

def create_summary_table(nodes_df, edges_df):
    """Create a summary table of FT-funded publications"""
    ft_papers = []
    
    for _, node in nodes_df.iterrows():
        if node['node_type'] == 'paper':
            details = parse_node_details(node['details'])
            if 'ft_grant' in details:
                ft_papers.append({
                    'Paper ID': node['node_id'],
                    'Title': details.get('title', 'N/A'),
                    'Authors': details.get('authors', 'N/A'),
                    'Year': details.get('year', 'N/A'),
                    'Journal': details.get('journal', 'N/A'),
                    'Distance to Approval': details.get('node_distance_to_approval', 'N/A')
                })
    
    return pd.DataFrame(ft_papers)

def main():
    # Header
    st.markdown('<h1 class="main-header">🧬 Research Grant to Treatment Lineage</h1>', unsafe_allow_html=True)
    
    # Load data
    nodes_df, edges_df = load_data()
    
    # Sidebar with information
    with st.sidebar:
        st.header("📊 Dataset Overview")
        
        total_nodes = len(nodes_df)
        total_papers = len(nodes_df[nodes_df['node_type'] == 'paper'])
        total_edges = len(edges_df)
        
        st.metric("Total Nodes", total_nodes)
        st.metric("Total Papers", total_papers)
        st.metric("Total Connections", total_edges)
        
        st.markdown("---")
        st.header("🎨 Color Legend")
        st.markdown("""
        - 🔵 **Blue**: FT Grant & Funded Papers
        - 🟠 **Orange**: Papers citing FT research
        - 🟢 **Green**: Approval Paper & Treatment
        - ⚪ **Grey**: Other Publications
        
        *Color intensity indicates distance to final approval*
        """)
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This visualization shows the path from a Fondazione Telethon research grant 
        through scientific publications to the final approved treatment (Givinostat).
        
        The graph demonstrates how initial research funding can lead to breakthrough 
        treatments through a network of scientific citations and collaborations.
        """)
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📈 Citation Network Visualization")
        
        # Create and display the network graph
        fig = create_network_graph(nodes_df, edges_df)
        st.plotly_chart(fig, use_container_width=True, height=600)
    
    with col2:
        st.subheader("📋 Quick Stats")
        
        # Calculate some interesting statistics
        ft_funded, citing_ft, approval, treatment = classify_nodes(nodes_df, edges_df)
        
        st.metric("FT-Funded Papers", len(ft_funded))
        st.metric("Papers Citing FT Research", len(citing_ft))
        st.metric("Approval Papers", len(approval))
        st.metric("Final Treatments", len(treatment))
        
        # Show treatment details
        treatment_node = nodes_df[nodes_df['node_type'] == 'treatment'].iloc[0]
        treatment_details = parse_node_details(treatment_node['details'])
        
        st.markdown("### 🎯 Final Treatment")
        st.markdown(f"**{treatment_node['node_label']}**")
        st.markdown(f"Approved: {treatment_details.get('approval_year', 'N/A')}")
        st.markdown(f"Agency: {treatment_details.get('approval_agency', 'N/A')}")
    
    # FT-funded publications table
    st.markdown("---")
    st.subheader("📚 Publications Funded by Fondazione Telethon")
    
    ft_table = create_summary_table(nodes_df, edges_df)
    if not ft_table.empty:
        st.dataframe(ft_table, use_container_width=True)
    else:
        st.info("No FT-funded publications found in the dataset.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9rem;'>
        <p>Exploring the Path from Research Grants to FDA and EMA Approved Treatments</p>
        <p>A Collaborative Approach to Understanding Research Impact</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
