
"""
Research Impact Dashboard - Streamlit App
Demonstrates how institutional funding leads to breakthrough treatments
Perfect for stakeholder presentations and fundraising demonstrations
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from plotly.subplots import make_subplots
import numpy as np

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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .network-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
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
    """Load data from SQLite database"""
    try:
        conn = sqlite3.connect('data/streamlit_research_database.db')
        nodes_df = pd.read_sql('SELECT * FROM nodes', conn)
        edges_df = pd.read_sql('SELECT * FROM edges', conn)
        summary_df = pd.read_sql('SELECT * FROM network_summary', conn)
        conn.close()
        return nodes_df, edges_df, summary_df
    except:
        # Fallback to CSV files if database not available
        nodes_df = pd.read_csv('data/streamlit_nodes.csv')
        edges_df = pd.read_csv('data/streamlit_edges.csv')
        summary_df = pd.read_csv('data/streamlit_summary.csv')
        return nodes_df, edges_df, summary_df

@st.cache_data
def calculate_roi_metrics(summary_df, nodes_df):
    """Calculate ROI and impact metrics"""
    total_funding = summary_df['funding_amount'].sum()
    total_publications = len(nodes_df[nodes_df['node_type'] == 'publication'])
    total_treatments = len(nodes_df[nodes_df['node_type'] == 'treatment'])
    
    # Calculate metrics
    cost_per_publication = total_funding / total_publications if total_publications > 0 else 0
    cost_per_treatment = total_funding / total_treatments if total_treatments > 0 else 0
    avg_research_duration = summary_df['research_duration'].mean()
    
    return {
        'total_funding': total_funding,
        'total_publications': total_publications,
        'total_treatments': total_treatments,
        'cost_per_publication': cost_per_publication,
        'cost_per_treatment': cost_per_treatment,
        'avg_research_duration': avg_research_duration,
        'success_rate': (total_treatments / len(summary_df)) * 100
    }

def create_network_graph(nodes_df, edges_df, selected_network):
    """Create interactive network visualization"""
    # Filter data for selected network
    network_nodes = nodes_df[nodes_df['network_id'] == selected_network]
    network_edges = edges_df[edges_df['network_id'] == selected_network]
    
    # Create NetworkX graph
    G = nx.DiGraph()
    
    # Add nodes
    for _, node in network_nodes.iterrows():
        G.add_node(node['node_id'], **node.to_dict())
    
    # Add edges
    for _, edge in network_edges.iterrows():
        G.add_edge(edge['source_id'], edge['target_id'], **edge.to_dict())
    
    # Create layout
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Prepare data for Plotly
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
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node traces by type
    node_traces = []
    colors = {
        'grant': '#1f77b4',
        'publication': '#ff7f0e', 
        'treatment': '#2ca02c'
    }
    
    for node_type in ['grant', 'publication', 'treatment']:
        type_nodes = network_nodes[network_nodes['node_type'] == node_type]
        if len(type_nodes) > 0:
            node_x = [pos[node_id][0] for node_id in type_nodes['node_id']]
            node_y = [pos[node_id][1] for node_id in type_nodes['node_id']]
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                text=[f"{row['node_type']}: {row.get('grant_id', row.get('pmid', row.get('treatment_name', 'Unknown')))}" 
                      for _, row in type_nodes.iterrows()],
                marker=dict(
                    size=20 if node_type == 'grant' else 15 if node_type == 'treatment' else 10,
                    color=colors[node_type],
                    line=dict(width=2, color='white')
                ),
                name=node_type.title()
            )
            node_traces.append(node_trace)
    
    # Create figure
    fig = go.Figure(data=[edge_trace] + node_traces,
                   layout=go.Layout(
                       title=f'Research Network: {network_nodes.iloc[0]["disease_focus"] if "disease_focus" in network_nodes.columns else "Network"}',
                       titlefont_size=16,
                       showlegend=True,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       annotations=[ dict(
                           text="Hover over nodes for details",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002,
                           xanchor="left", yanchor="bottom",
                           font=dict(color="#888", size=12)
                       )],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                   ))
    
    return fig

def create_timeline_chart(summary_df):
    """Create timeline visualization"""
    fig = go.Figure()
    
    for _, network in summary_df.iterrows():
        # Grant start
        fig.add_trace(go.Scatter(
            x=[network['grant_year']],
            y=[network['disease']],
            mode='markers',
            marker=dict(size=15, color='blue', symbol='diamond'),
            name=f"Grant Start",
            showlegend=False,
            hovertemplate=f"<b>{network['disease']}</b><br>Grant: {network['grant_year']}<br>Funding: ${network['funding_amount']:,.0f}<extra></extra>"
        ))
        
        # Treatment approval
        fig.add_trace(go.Scatter(
            x=[network['approval_year']],
            y=[network['disease']],
            mode='markers',
            marker=dict(size=20, color='green', symbol='star'),
            name=f"Treatment Approved",
            showlegend=False,
            hovertemplate=f"<b>{network['treatment_name']}</b><br>Approved: {network['approval_year']}<br>Duration: {network['research_duration']} years<extra></extra>"
        ))
        
        # Timeline line
        fig.add_trace(go.Scatter(
            x=[network['grant_year'], network['approval_year']],
            y=[network['disease'], network['disease']],
            mode='lines',
            line=dict(color='gray', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        title="Research Timeline: From Grant to Treatment",
        xaxis_title="Year",
        yaxis_title="Disease Area",
        height=400,
        hovermode='closest'
    )
    
    return fig

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔬 Research Impact Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Demonstrating How Institutional Funding Creates Breakthrough Treatments</p>', unsafe_allow_html=True)
    
    # Load data
    try:
        nodes_df, edges_df, summary_df = load_database()
        roi_metrics = calculate_roi_metrics(summary_df, nodes_df)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please ensure the database files are in the 'data/' directory")
        return
    
    # Sidebar
    st.sidebar.title("🎯 Dashboard Controls")
    
    # Network selector
    selected_network = st.sidebar.selectbox(
        "Select Research Network:",
        options=summary_df['network_id'].tolist(),
        format_func=lambda x: f"{summary_df[summary_df['network_id']==x]['disease'].iloc[0]} Research"
    )
    
    # Show/hide sections
    show_overview = st.sidebar.checkbox("📊 Overview Metrics", value=True)
    show_networks = st.sidebar.checkbox("🔬 Network Details", value=True)
    show_timeline = st.sidebar.checkbox("📅 Research Timeline", value=True)
    show_visualization = st.sidebar.checkbox("🕸️ Network Graph", value=True)
    
    # Overview Metrics
    if show_overview:
        st.header("📊 Research Impact Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Investment",
                f"${roi_metrics['total_funding']:,.0f}",
                help="Total institutional funding across all research networks"
            )
        
        with col2:
            st.metric(
                "Publications Generated",
                f"{roi_metrics['total_publications']:,}",
                help="Total research publications produced"
            )
        
        with col3:
            st.metric(
                "Treatments Approved",
                f"{roi_metrics['total_treatments']}",
                help="Number of breakthrough treatments developed"
            )
        
        with col4:
            st.metric(
                "Success Rate",
                f"{roi_metrics['success_rate']:.0f}%",
                help="Percentage of grants leading to approved treatments"
            )
        
        # ROI Metrics
        st.subheader("💰 Return on Investment")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Cost per Publication",
                f"${roi_metrics['cost_per_publication']:,.0f}",
                help="Average funding required per research publication"
            )
        
        with col2:
            st.metric(
                "Cost per Treatment",
                f"${roi_metrics['cost_per_treatment']:,.0f}",
                help="Average funding required per approved treatment"
            )
        
        with col3:
            st.metric(
                "Avg. Research Duration",
                f"{roi_metrics['avg_research_duration']:.1f} years",
                help="Average time from grant to treatment approval"
            )
    
    # Network Details
    if show_networks:
        st.header("🔬 Research Network Details")
        
        for _, network in summary_df.iterrows():
            with st.expander(f"🧬 {network['disease']} Research Network", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📋 Grant Information**")
                    st.write(f"**Grant ID:** {network['grant_id']}")
                    st.write(f"**Funding Amount:** ${network['funding_amount']:,.0f}")
                    st.write(f"**Grant Year:** {network['grant_year']}")
                    st.write(f"**Research Duration:** {network['research_duration']} years")
                
                with col2:
                    st.markdown("**🎯 Treatment Outcome**")
                    st.write(f"**Treatment:** {network['treatment_name']}")
                    st.write(f"**Approval Year:** {network['approval_year']}")
                    st.write(f"**Publications:** {network['total_publications']}")
                    st.markdown(f"<p class='success-metric'>✅ Successfully Approved</p>", unsafe_allow_html=True)
    
    # Timeline Visualization
    if show_timeline:
        st.header("📅 Research Timeline")
        timeline_fig = create_timeline_chart(summary_df)
        st.plotly_chart(timeline_fig, use_container_width=True)
    
    # Network Visualization
    if show_visualization:
        st.header("🕸️ Citation Network Visualization")
        
        network_fig = create_network_graph(nodes_df, edges_df, selected_network)
        st.plotly_chart(network_fig, use_container_width=True)
        
        # Network statistics
        network_nodes = nodes_df[nodes_df['network_id'] == selected_network]
        network_edges = edges_df[edges_df['network_id'] == selected_network]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Network Nodes", len(network_nodes))
        
        with col2:
            st.metric("Connections", len(network_edges))
        
        with col3:
            publications = len(network_nodes[network_nodes['node_type'] == 'publication'])
            st.metric("Publications", publications)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <h4>🎯 Demonstrating Research Impact</h4>
        <p>This dashboard shows how institutional funding directly leads to breakthrough treatments,<br>
        providing clear evidence of research ROI for stakeholders and donors.</p>
        <p><strong>Ready to secure more funding for life-saving research!</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
