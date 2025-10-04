"""
Research Impact Dashboard - Elegant Graph Version
Beautiful network visualization matching the Drawing.pdf style
Clean, organized, and professional presentation
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import networkx as nx
import numpy as np
import os
import math

# Page configuration
st.set_page_config(
    page_title="Research Impact Dashboard",
    page_icon="🔬",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
.main-header { font-size: 3rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; }
.selection-card { background-color: #f8f9fa; padding: 2rem; border-radius: 1rem; border: 2px solid #e9ecef; margin: 1rem 0; text-align: center; }
.grant-card { border-left: 6px solid #007bff; }
.treatment-card { border-left: 6px solid #28a745; }
.metric-highlight { font-size: 1.5rem; font-weight: bold; color: #495057; }
.success-metric { color: #28a745; font-weight: bold; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_database():
    """Load data from files"""
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
        return create_sample_data()

def create_sample_data():
    """Create sample data"""
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

def create_elegant_network(nodes_df, edges_df, network_id):
    """Create elegant network visualization matching Drawing.pdf style"""
    try:
        network_nodes = nodes_df[nodes_df['network_id'] == network_id]
        network_edges = edges_df[edges_df['network_id'] == network_id]
        
        if len(network_nodes) == 0:
            return go.Figure()
        
        # Separate nodes by type
        grants = network_nodes[network_nodes['node_type'] == 'grant']
        treatments = network_nodes[network_nodes['node_type'] == 'treatment']
        publications = network_nodes[network_nodes['node_type'] == 'publication']
        
        # Create elegant layout matching Drawing.pdf
        node_positions = {}
        
        # 1. Position FT_Grant (large blue circle) on the left
        if len(grants) > 0:
            grant_node = grants.iloc[0]
            node_positions[grant_node['node_id']] = (-4, 0)
        
        # 2. Position initial funded publications (gray circles) - 4 nodes connected to grant
        initial_pubs = publications.head(4) if len(publications) >= 4 else publications
        for i, (_, pub) in enumerate(initial_pubs.iterrows()):
            y_pos = 1.5 - (i * 1.0)  # Spread vertically: 1.5, 0.5, -0.5, -1.5
            node_positions[pub['node_id']] = (-2, y_pos)
        
        # 3. Position research ecosystem (white circles) - scattered in middle area
        research_pubs = publications.iloc[4:] if len(publications) > 4 else pd.DataFrame()
        np.random.seed(42)  # For consistent layout
        
        # Create organized clusters in the research area
        research_area_x = np.linspace(-1, 3, len(research_pubs)) if len(research_pubs) > 0 else []
        research_area_y = []
        
        for i in range(len(research_pubs)):
            # Create gentle waves and clusters
            base_y = 0.8 * math.sin(i * 0.5) + np.random.normal(0, 0.3)
            research_area_y.append(base_y)
        
        for i, (_, pub) in enumerate(research_pubs.iterrows()):
            if i < len(research_area_x):
                x_pos = research_area_x[i] + np.random.normal(0, 0.2)
                y_pos = research_area_y[i]
                node_positions[pub['node_id']] = (x_pos, y_pos)
        
        # 4. Position treatment pathway nodes (yellow circles) - leading to treatment
        treatment_pubs = publications.tail(3) if len(publications) >= 3 else publications.tail(len(publications))
        for i, (_, pub) in enumerate(treatment_pubs.iterrows()):
            y_pos = 0.8 - (i * 0.8)  # Spread vertically near treatment
            node_positions[pub['node_id']] = (4, y_pos)
        
        # 5. Position final treatment (large green circle) on the right
        if len(treatments) > 0:
            treatment_node = treatments.iloc[0]
            node_positions[treatment_node['node_id']] = (6, 0)
        
        # Create clean, organized edges (no spaghetti!)
        edge_traces = []
        
        # Define edge styles matching Drawing.pdf
        edge_styles = {
            'funded_by': {'color': '#2E86AB', 'width': 3, 'dash': None},
            'cites': {'color': '#A23B72', 'width': 1, 'dash': 'dot'},
            'leads_to_treatment': {'color': '#F18F01', 'width': 2, 'dash': None},
            'enables_treatment': {'color': '#C73E1D', 'width': 3, 'dash': None}
        }
        
        # Group edges by type for clean rendering
        edge_types = network_edges['edge_type'].unique() if 'edge_type' in network_edges.columns else ['connection']
        
        for edge_type in edge_types:
            type_edges = network_edges[network_edges['edge_type'] == edge_type] if 'edge_type' in network_edges.columns else network_edges
            
            edge_x = []
            edge_y = []
            
            for _, edge in type_edges.iterrows():
                if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    
                    # Create smooth curved lines for elegance
                    if abs(x1 - x0) > 2:  # Long connections get curves
                        # Add curve control points
                        mid_x = (x0 + x1) / 2
                        mid_y = (y0 + y1) / 2 + 0.3 * math.sin((x1 - x0) * 0.5)
                        
                        # Create smooth curve with multiple points
                        curve_points = 10
                        for i in range(curve_points + 1):
                            t = i / curve_points
                            # Quadratic Bezier curve
                            curve_x = (1-t)**2 * x0 + 2*(1-t)*t * mid_x + t**2 * x1
                            curve_y = (1-t)**2 * y0 + 2*(1-t)*t * mid_y + t**2 * y1
                            edge_x.append(curve_x)
                            edge_y.append(curve_y)
                        edge_x.append(None)
                        edge_y.append(None)
                    else:  # Short connections are straight
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
            
            if edge_x:
                style = edge_styles.get(edge_type, {'color': '#888', 'width': 1, 'dash': None})
                
                edge_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(
                        width=style['width'], 
                        color=style['color'],
                        dash=style['dash']
                    ),
                    hoverinfo='none',
                    mode='lines',
                    name=edge_type.replace('_', ' ').title(),
                    showlegend=True,
                    opacity=0.7
                )
                edge_traces.append(edge_trace)
        
        # Create beautiful node traces
        node_traces = []
        
        # Define elegant colors and sizes matching Drawing.pdf
        node_styles = {
            'grant': {
                'color': '#1f4e79',  # Deep blue
                'size': 40,
                'line_color': '#ffffff',
                'line_width': 3
            },
            'publication': {
                'color': '#d1d5db',  # Light gray (white circles in drawing)
                'size': 12,
                'line_color': '#6b7280',
                'line_width': 1
            },
            'treatment': {
                'color': '#059669',  # Green
                'size': 35,
                'line_color': '#ffffff',
                'line_width': 3
            }
        }
        
        # Special styling for key pathway nodes (yellow in drawing)
        treatment_pathway_nodes = treatment_pubs['node_id'].tolist() if len(treatment_pubs) > 0 else []
        
        for node_type in ['grant', 'publication', 'treatment']:
            type_nodes = network_nodes[network_nodes['node_type'] == node_type]
            
            if len(type_nodes) > 0:
                node_x = []
                node_y = []
                node_text = []
                node_colors = []
                node_sizes = []
                
                for _, node in type_nodes.iterrows():
                    if node['node_id'] in node_positions:
                        x, y = node_positions[node['node_id']]
                        node_x.append(x)
                        node_y.append(y)
                        
                        # Special styling for treatment pathway nodes
                        if node['node_id'] in treatment_pathway_nodes:
                            node_colors.append('#fbbf24')  # Yellow for treatment pathway
                            node_sizes.append(18)
                        else:
                            node_colors.append(node_styles[node_type]['color'])
                            node_sizes.append(node_styles[node_type]['size'])
                        
                        # Create informative hover text
                        if node_type == 'grant':
                            text = "🔵 GRANT<br>" + str(node.get('grant_id', node['node_id']))
                            text += "<br>Funding Source"
                        elif node_type == 'treatment':
                            text = "🟢 TREATMENT<br>" + str(node.get('treatment_name', node['node_id']))
                            text += "<br>FDA Approved"
                        else:  # publication
                            if node['node_id'] in treatment_pathway_nodes:
                                text = "🟡 KEY RESEARCH<br>PMID: " + str(node.get('pmid', node['node_id']))
                                text += "<br>Treatment Pathway"
                            else:
                                text = "⚪ RESEARCH<br>PMID: " + str(node.get('pmid', node['node_id']))
                                text += "<br>Supporting Research"
                        
                        node_text.append(text)
                
                if node_x:
                    # Create separate traces for different node colors
                    unique_colors = list(set(node_colors))
                    
                    for color in unique_colors:
                        color_indices = [i for i, c in enumerate(node_colors) if c == color]
                        
                        if color_indices:
                            trace_x = [node_x[i] for i in color_indices]
                            trace_y = [node_y[i] for i in color_indices]
                            trace_text = [node_text[i] for i in color_indices]
                            trace_sizes = [node_sizes[i] for i in color_indices]
                            
                            # Determine trace name
                            if color == '#fbbf24':  # Yellow
                                trace_name = "Treatment Pathway"
                            elif node_type == 'grant':
                                trace_name = "Research Grant"
                            elif node_type == 'treatment':
                                trace_name = "Breakthrough Treatment"
                            else:
                                trace_name = "Research Publications"
                            
                            node_trace = go.Scatter(
                                x=trace_x, y=trace_y,
                                mode='markers',
                                hoverinfo='text',
                                text=trace_text,
                                marker=dict(
                                    size=trace_sizes,
                                    color=color,
                                    line=dict(
                                        width=node_styles[node_type]['line_width'],
                                        color=node_styles[node_type]['line_color']
                                    ),
                                    opacity=0.9
                                ),
                                name=trace_name,
                                showlegend=True
                            )
                            node_traces.append(node_trace)
        
        # Create the elegant figure
        fig = go.Figure(data=edge_traces + node_traces)
        
        fig.update_layout(
            title={
                'text': "Research Impact Network",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#1f4e79'}
            },
            showlegend=True,
            hovermode='closest',
            margin=dict(b=40, l=40, r=40, t=60),
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-5, 7]
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-3, 3]
            ),
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1
            )
        )
        
        return fig
    
    except Exception as e:
        st.error("Error creating elegant network: " + str(e))
        return go.Figure()

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔬 Research Impact Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Explore Research Networks by Grant or Treatment</p>', unsafe_allow_html=True)
    
    # Load data
    nodes_df, edges_df, summary_df = load_database()
    
    # STEP 1: Choose exploration method
    st.header("🎯 How would you like to explore the research?")
    
    # Radio button for selection method
    exploration_method = st.radio(
        "Choose your exploration method:",
        options=["Select by Grant (Funding Source)", "Select by Treatment (Research Outcome)"],
        index=0,
        help="Choose whether to start from the funding source or the final treatment outcome"
    )
    
    s
(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)
