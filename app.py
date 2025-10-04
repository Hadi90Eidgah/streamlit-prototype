"""
Research Impact Dashboard - Fixed Connections
Properly displays leads_to_treatment edges showing grant impact
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import numpy as np
import os
import math

# Page configuration
st.set_page_config(
    page_title="Research Impact Dashboard",
    page_icon="🔬",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.main-header { font-size: 3rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; }
.selection-card { background-color: #f8f9fa; padding: 2rem; border-radius: 1rem; border: 2px solid #e9ecef; margin: 1rem 0; text-align: center; }
.grant-card { border-left: 6px solid #007bff; }
.treatment-card { border-left: 6px solid #28a745; }
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

def create_fixed_network(nodes_df, edges_df, network_id):
    """Create network visualization with properly displayed connections"""
    try:
        network_nodes = nodes_df[nodes_df['network_id'] == network_id]
        network_edges = edges_df[edges_df['network_id'] == network_id]
        
        if len(network_nodes) == 0:
            return go.Figure()
        
        # Separate nodes by type
        grants = network_nodes[network_nodes['node_type'] == 'grant']
        treatments = network_nodes[network_nodes['node_type'] == 'treatment']
        publications = network_nodes[network_nodes['node_type'] == 'publication']
        
        # Create layout with better positioning
        node_positions = {}
        
        # Position grant (large blue circle) on the left
        grant_node_id = None
        if len(grants) > 0:
            grant_node = grants.iloc[0]
            grant_node_id = grant_node['node_id']
            node_positions[grant_node_id] = (-5, 0)
        
        # Identify different types of publications
        grant_funded_pubs = []
        treatment_pathway_pubs = []
        ecosystem_pubs = []
        
        for _, pub in publications.iterrows():
            pub_id = pub['node_id']
            if pub_id.startswith('PUB_'):
                grant_funded_pubs.append(pub_id)
            elif pub_id.startswith('TREAT_PUB_'):
                treatment_pathway_pubs.append(pub_id)
            elif pub_id.startswith('ECO_'):
                ecosystem_pubs.append(pub_id)
        
        # Position grant-funded publications (directly connected to grant)
        for i, pub_id in enumerate(grant_funded_pubs):
            y_pos = 2 - (i * 1.3)
            node_positions[pub_id] = (-2.5, y_pos)
        
        # Position ecosystem publications in organized clusters
        np.random.seed(42)
        cluster_centers = [(-0.5, 1), (0.5, 0.5), (1.5, -0.5), (0, -1.5)]
        
        for i, pub_id in enumerate(ecosystem_pubs):
            cluster_idx = i % len(cluster_centers)
            center_x, center_y = cluster_centers[cluster_idx]
            x_pos = center_x + np.random.normal(0, 0.4)
            y_pos = center_y + np.random.normal(0, 0.4)
            node_positions[pub_id] = (x_pos, y_pos)
        
        # Position treatment pathway publications
        for i, pub_id in enumerate(treatment_pathway_pubs):
            y_pos = 1 - (i * 1.0)
            node_positions[pub_id] = (3.5, y_pos)
        
        # Position treatment on the right
        treatment_node_id = None
        if len(treatments) > 0:
            treatment_node = treatments.iloc[0]
            treatment_node_id = treatment_node['node_id']
            node_positions[treatment_node_id] = (6, 0)
        
        # Create edge traces with FIXED categorization
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
                    line=dict(width=4, color='rgba(31, 78, 121, 0.9)'),
                    hoverinfo='none',
                    mode='lines',
                    name='🔵 Grant Funding',
                    showlegend=True
                )
                edge_traces.append(grant_trace)
        
        # 2. Treatment pathway edges (yellow, medium) - FIXED!
        treatment_pathway_edges = network_edges[network_edges['edge_type'] == 'leads_to_treatment']
        if len(treatment_pathway_edges) > 0:
            edge_x, edge_y = [], []
            for _, edge in treatment_pathway_edges.iterrows():
                if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            if edge_x:
                treatment_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=3, color='rgba(251, 191, 36, 0.8)'),
                    hoverinfo='none',
                    mode='lines',
                    name='🟡 Treatment Impact',
                    showlegend=True
                )
                edge_traces.append(treatment_trace)
        
        # 3. Treatment enablement edges (green, medium)
        treatment_enable_edges = network_edges[network_edges['edge_type'] == 'enables_treatment']
        if len(treatment_enable_edges) > 0:
            edge_x, edge_y = [], []
            for _, edge in treatment_enable_edges.iterrows():
                if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            if edge_x:
                enable_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=3, color='rgba(5, 150, 105, 0.8)'),
                    hoverinfo='none',
                    mode='lines',
                    name='🟢 Enables Treatment',
                    showlegend=True
                )
                edge_traces.append(enable_trace)
        
        # 4. General citation edges (gray, transparent)
        citation_edges = network_edges[network_edges['edge_type'] == 'cites']
        if len(citation_edges) > 0:
            edge_x, edge_y = [], []
            for _, edge in citation_edges.iterrows():
                if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            if edge_x:
                citation_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=1, color='rgba(200, 200, 200, 0.3)'),
                    hoverinfo='none',
                    mode='lines',
                    showlegend=False
                )
                edge_traces.append(citation_trace)
        
        # Create node traces
        node_traces = []
        
        # Grant nodes
        if len(grants) > 0:
            grant_x = [node_positions[grants.iloc[0]['node_id']][0]]
            grant_y = [node_positions[grants.iloc[0]['node_id']][1]]
            
            grant_trace = go.Scatter(
                x=grant_x, y=grant_y,
                mode='markers',
                hoverinfo='text',
                text=["🔵 RESEARCH GRANT<br>Funding Source"],
                marker=dict(size=45, color='#1f4e79', line=dict(width=3, color='white')),
                name='🔵 Research Grant',
                showlegend=True
            )
            node_traces.append(grant_trace)
        
        # Grant-funded publication nodes
        if grant_funded_pubs:
            pub_x = [node_positions[pub_id][0] for pub_id in grant_funded_pubs if pub_id in node_positions]
            pub_y = [node_positions[pub_id][1] for pub_id in grant_funded_pubs if pub_id in node_positions]
            
            if pub_x:
                funded_pub_trace = go.Scatter(
                    x=pub_x, y=pub_y,
                    mode='markers',
                    hoverinfo='text',
                    text=["⚪ GRANT-FUNDED RESEARCH<br>Direct Impact"] * len(pub_x),
                    marker=dict(size=16, color='#e5e7eb', line=dict(width=2, color='white')),
                    name='⚪ Grant-Funded Research',
                    showlegend=True
                )
                node_traces.append(funded_pub_trace)
        
        # Ecosystem publication nodes
        if ecosystem_pubs:
            eco_x = [node_positions[pub_id][0] for pub_id in ecosystem_pubs if pub_id in node_positions]
            eco_y = [node_positions[pub_id][1] for pub_id in ecosystem_pubs if pub_id in node_positions]
            
            if eco_x:
                eco_trace = go.Scatter(
                    x=eco_x, y=eco_y,
                    mode='markers',
                    hoverinfo='text',
                    text=["⚪ RESEARCH ECOSYSTEM<br>Citing Grant Work"] * len(eco_x),
                    marker=dict(size=12, color='#f3f4f6', line=dict(width=1, color='white')),
                    name='⚪ Research Ecosystem',
                    showlegend=True
                )
                node_traces.append(eco_trace)
        
        # Treatment pathway nodes
        if treatment_pathway_pubs:
            treat_x = [node_positions[pub_id][0] for pub_id in treatment_pathway_pubs if pub_id in node_positions]
            treat_y = [node_positions[pub_id][1] for pub_id in treatment_pathway_pubs if pub_id in node_positions]
            
            if treat_x:
                pathway_trace = go.Scatter(
                    x=treat_x, y=treat_y,
                    mode='markers',
                    hoverinfo='text',
                    text=["🟡 TREATMENT DEVELOPMENT<br>Cites Grant Research"] * len(treat_x),
                    marker=dict(size=20, color='#fbbf24', line=dict(width=2, color='white')),
                    name='🟡 Treatment Development',
                    showlegend=True
                )
                node_traces.append(pathway_trace)
        
        # Treatment nodes
        if len(treatments) > 0:
            treatment_x = [node_positions[treatments.iloc[0]['node_id']][0]]
            treatment_y = [node_positions[treatments.iloc[0]['node_id']][1]]
            
            treatment_trace = go.Scatter(
                x=treatment_x, y=treatment_y,
                mode='markers',
                hoverinfo='text',
                text=["🟢 BREAKTHROUGH TREATMENT<br>FDA Approved"],
                marker=dict(size=40, color='#059669', line=dict(width=3, color='white')),
                name='🟢 Breakthrough Treatment',
                showlegend=True
            )
            node_traces.append(treatment_trace)
        
        # Create figure
        fig = go.Figure(data=edge_traces + node_traces)
        
        fig.update_layout(
            title={
                'text': "Research Impact Network - Grant to Treatment Flow",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#1f4e79', 'family': 'Arial Black'}
            },
            showlegend=True,
            hovermode='closest',
            margin=dict(b=50, l=50, r=50, t=80),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-6, 7]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-3, 3]),
            height=650,
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(
                yanchor="top", y=0.98, xanchor="left", x=0.02,
                bgcolor="rgba(255,255,255,0.9)", bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1, font=dict(size=12)
            )
        )
        
        return fig
    
    except Exception as e:
        st.error("Error creating network: " + str(e))
        return go.Figure()

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔬 Research Impact Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Demonstrating Grant Impact Through Research Networks</p>', unsafe_allow_html=True)
    
    # Load data
    nodes_df, edges_df, summary_df = load_database()
    
    # Debug info
    with st.expander("🔍 Debug: Connection Analysis"):
        st.write("**Edge Types in Dataset:**")
        edge_types = edges_df['edge_type'].value_counts()
        st.write(edge_types)
        
        st.write("**Sample Treatment Impact Connections:**")
        treatment_edges = edges_df[edges_df['edge_type'] == 'leads_to_treatment'].head(5)
        st.dataframe(treatment_edges)
    
    # Choose exploration method
    st.header("🎯 How would you like to explore the research?")
    
    exploration_method = st.radio(
        "Choose your exploration method:",
        options=["Select by Grant (Funding Source)", "Select by Treatment (Research Outcome)"],
        index=0
    )
    
    st.markdown("---")
    
    # Show selection interface
    selected_network_id = None
    
    if exploration_method == "Select by Grant (Funding Source)":
        st.header("📋 Select Research Grant")
        
        grant_options = {}
        for _, row in summary_df.iterrows():
            option_text = str(row['grant_id']) + " - " + str(row['disease']) + " Research"
            grant_options[option_text] = row['network_id']
        
        selected_grant = st.selectbox("Choose a research grant:", options=list(grant_options.keys()))
        
        if selected_grant:
            selected_network_id = grant_options[selected_grant]
            grant_info = summary_df[summary_df['network_id'] == selected_network_id].iloc[0]
            
            st.success(f"✅ Selected: {grant_info['grant_id']} - ${grant_info['funding_amount']:,.0f} → {grant_info['treatment_name']}")
    
    else:
        st.header("🎯 Select Breakthrough Treatment")
        
        treatment_options = {}
        for _, row in summary_df.iterrows():
            option_text = str(row['treatment_name']) + " - " + str(row['disease'])
            treatment_options[option_text] = row['network_id']
        
        selected_treatment = st.selectbox("Choose a treatment:", options=list(treatment_options.keys()))
        
        if selected_treatment:
            selected_network_id = treatment_options[selected_treatment]
            treatment_info = summary_df[summary_df['network_id'] == selected_network_id].iloc[0]
            
            st.success(f"✅ Selected: {treatment_info['treatment_name']} ← ${treatment_info['funding_amount']:,.0f} grant")
    
    # Show network with fixed connections
    if selected_network_id:
        st.markdown("---")
        st.header("🕸️ Research Impact Network")
        
        # Show the fixed network
        fig = create_fixed_network(nodes_df, edges_df, selected_network_id)
        st.plotly_chart(fig, width='stretch')
        
        # Enhanced explanation
        st.info("""
        **🎯 Key Connections to Look For:**
        - **🔵 Blue thick lines** = Grant directly funds research
        - **🟡 Yellow lines** = Treatment development cites grant-funded research (IMPACT!)
        - **🟢 Green lines** = Research enables final treatment
        - **Gray thin lines** = General research citations (background)
        
        **The yellow lines show how grant-funded research directly contributed to treatment development!**
        """)
        
        # Connection analysis
        network_edges = edges_df[edges_df['network_id'] == selected_network_id]
        treatment_impact_edges = network_edges[network_edges['edge_type'] == 'leads_to_treatment']
        
        st.subheader("📊 Grant Impact Analysis")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            grant_funding = len(network_edges[network_edges['edge_type'] == 'funded_by'])
            st.metric("Grant-Funded Papers", grant_funding)
        
        with col2:
            st.metric("Treatment Impact Citations", len(treatment_impact_edges))
        
        with col3:
            impact_percentage = (len(treatment_impact_edges) / grant_funding * 100) if grant_funding > 0 else 0
            st.metric("Impact Rate", f"{impact_percentage:.0f}%")
        
        if len(treatment_impact_edges) > 0:
            st.success(f"🎯 **SUCCESS**: Treatment development cited {len(treatment_impact_edges)} grant-funded publications!")
        else:
            st.warning("⚠️ No treatment impact connections found in visualization")

if __name__ == "__main__":
    main()
