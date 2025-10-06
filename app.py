"""
Research Impact Dashboard - FIXED Treatment Connections
Properly displays leads_to_treatment edges from TREAT_PUB nodes to PUB nodes
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

# CSS
st.markdown("""
<style>
.main-header { font-size: 3rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; }
.selection-card { background-color: #f8f9fa; padding: 2rem; border-radius: 1rem; border: 2px solid #e9ecef; margin: 1rem 0; text-align: center; }
.grant-card { border-left: 6px solid #007bff; }
.treatment-card { border-left: 6px solid #28a745; }
.success-metric { color: #28a745; font-weight: bold; font-size: 1.2rem; }
.network-info { background-color: #f0f8ff; padding: 1.5rem; border-radius: 0.8rem; border: 1px solid #b0d4f1; margin: 1rem 0; }
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

def create_network_visualization(nodes_df, edges_df, network_id):
    """Create network visualization with FIXED treatment pathway connections"""
    try:
        # Filter data for selected network
        network_nodes = nodes_df[nodes_df['network_id'] == network_id].copy()
        network_edges = edges_df[edges_df['network_id'] == network_id].copy()
        
        if len(network_nodes) == 0:
            st.error(f"No data found for network {network_id}")
            return go.Figure()
        
        # Debug info
        st.write(f"**Network {network_id} Data:** {len(network_nodes)} nodes, {len(network_edges)} edges")
        
        # Separate nodes by type and specific patterns
        grants = network_nodes[network_nodes['node_type'] == 'grant']
        treatments = network_nodes[network_nodes['node_type'] == 'treatment']
        publications = network_nodes[network_nodes['node_type'] == 'publication']
        
        # CRITICAL: Properly categorize publications
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
        
        # Debug publication categorization
        st.write(f"**Publication Categories:**")
        st.write(f"- Grant-funded: {len(grant_funded_pubs)} ({grant_funded_pubs[:3]}...)")
        st.write(f"- Treatment pathway: {len(treatment_pathway_pubs)} ({treatment_pathway_pubs})")
        st.write(f"- Ecosystem: {len(ecosystem_pubs)} (first 3: {ecosystem_pubs[:3]})")
        
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
        
        # CRITICAL: Position treatment pathway publications (yellow circles on the right)
        for i, pub_id in enumerate(treatment_pathway_pubs):
            y_pos = 1 - (i * 1.0)
            node_positions[pub_id] = (3.5, y_pos)
        
        # Position treatment (green circle) on the far right
        if len(treatments) > 0:
            treatment_node = treatments.iloc[0]
            treatment_node_id = treatment_node['node_id']
            node_positions[treatment_node_id] = (6, 0)
        
        # Debug node positions
        st.write(f"**Node Positions Created:** {len(node_positions)}")
        
        # Create edge traces with FIXED logic
        edge_traces = []
        
        # 1. Grant funding edges (blue, thick)
        grant_funding_edges = network_edges[network_edges['edge_type'] == 'funded_by']
        if len(grant_funding_edges) > 0:
            edge_x, edge_y = [], []
            valid_count = 0
            
            for _, edge in grant_funding_edges.iterrows():
                if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    valid_count += 1
            
            st.write(f"- Grant funding edges: {valid_count}/{len(grant_funding_edges)} valid")
            
            if edge_x:
                grant_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=4, color='rgba(31, 78, 121, 0.9)'),
                    hoverinfo='none',
                    mode='lines',
                    name='Grant Funding',
                    showlegend=True
                )
                edge_traces.append(grant_trace)
        
        # 2. CRITICAL: Treatment pathway edges (yellow, thick) - FIXED!
        treatment_pathway_edges = network_edges[network_edges['edge_type'] == 'leads_to_treatment']
        if len(treatment_pathway_edges) > 0:
            edge_x, edge_y = [], []
            valid_count = 0
            
            st.write(f"**Processing {len(treatment_pathway_edges)} treatment pathway edges:**")
            
            for _, edge in treatment_pathway_edges.iterrows():
                source_id = edge['source_id']
                target_id = edge['target_id']
                
                if source_id in node_positions and target_id in node_positions:
                    x0, y0 = node_positions[source_id]
                    x1, y1 = node_positions[target_id]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    valid_count += 1
                    st.write(f"  ✅ {source_id} → {target_id}: ({x0:.1f},{y0:.1f}) → ({x1:.1f},{y1:.1f})")
                else:
                    missing = []
                    if source_id not in node_positions:
                        missing.append(f"source:{source_id}")
                    if target_id not in node_positions:
                        missing.append(f"target:{target_id}")
                    st.write(f"  ❌ {source_id} → {target_id}: Missing {', '.join(missing)}")
            
            st.write(f"- Treatment pathway edges: {valid_count}/{len(treatment_pathway_edges)} valid")
            
            if edge_x:
                treatment_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=4, color='rgba(255, 165, 0, 0.9)'),  # Thick orange
                    hoverinfo='none',
                    mode='lines',
                    name='Treatment Impact (CRITICAL)',
                    showlegend=True
                )
                edge_traces.append(treatment_trace)
                st.success(f"✅ Created treatment pathway trace with {len(edge_x)//3} edges")
            else:
                st.error("❌ No treatment pathway edges created - check node positions!")
        else:
            st.error("❌ No treatment pathway edges found in data!")
        
        # 3. General citation edges (gray, transparent)
        citation_edges = network_edges[network_edges['edge_type'] == 'cites']
        if len(citation_edges) > 0:
            edge_x, edge_y = [], []
            valid_count = 0
            
            for _, edge in citation_edges.iterrows():
                if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
                    x0, y0 = node_positions[edge['source_id']]
                    x1, y1 = node_positions[edge['target_id']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    valid_count += 1
            
            st.write(f"- Citation edges: {valid_count}/{len(citation_edges)} valid")
            
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
        
        # Grant nodes (blue)
        if len(grants) > 0:
            grant_x = [node_positions[grants.iloc[0]['node_id']][0]]
            grant_y = [node_positions[grants.iloc[0]['node_id']][1]]
            
            grant_trace = go.Scatter(
                x=grant_x, y=grant_y,
                mode='markers',
                hoverinfo='text',
                text=["Research Grant<br>Funding Source"],
                marker=dict(size=45, color='#1f4e79', line=dict(width=3, color='white')),
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
                    marker=dict(size=20, color='#e5e7eb', line=dict(width=2, color='white')),
                    name='Grant-Funded Research',
                    showlegend=True
                )
                node_traces.append(funded_pub_trace)
        
        # Treatment pathway nodes (yellow/orange)
        if treatment_pathway_pubs:
            treat_x = [node_positions[pub_id][0] for pub_id in treatment_pathway_pubs if pub_id in node_positions]
            treat_y = [node_positions[pub_id][1] for pub_id in treatment_pathway_pubs if pub_id in node_positions]
            
            if treat_x:
                pathway_trace = go.Scatter(
                    x=treat_x, y=treat_y,
                    mode='markers',
                    hoverinfo='text',
                    text=["Treatment Development<br>Cites Grant Research"] * len(treat_x),
                    marker=dict(size=25, color='#ffa500', line=dict(width=3, color='white')),
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
                    text=["Research Ecosystem<br>Citing Grant Work"] * len(eco_x),
                    marker=dict(size=12, color='#f3f4f6', line=dict(width=1, color='white')),
                    name='Research Ecosystem',
                    showlegend=True
                )
                node_traces.append(eco_trace)
        
        # Treatment nodes (green)
        if len(treatments) > 0:
            treatment_x = [node_positions[treatments.iloc[0]['node_id']][0]]
            treatment_y = [node_positions[treatments.iloc[0]['node_id']][1]]
            
            treatment_trace = go.Scatter(
                x=treatment_x, y=treatment_y,
                mode='markers',
                hoverinfo='text',
                text=["Breakthrough Treatment<br>FDA Approved"],
                marker=dict(size=40, color='#059669', line=dict(width=3, color='white')),
                name='Breakthrough Treatment',
                showlegend=True
            )
            node_traces.append(treatment_trace)
        
        # Create figure
        fig = go.Figure(data=edge_traces + node_traces)
        
        fig.update_layout(
            title={
                'text': f"Research Impact Network - {network_id} (FIXED)",
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
    st.markdown('<h1 class="main-header">Research Impact Dashboard - FIXED</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Now Shows Treatment → Grant Connections!</p>', unsafe_allow_html=True)
    
    # Load data
    nodes_df, edges_df, summary_df = load_database()
    
    # Database verification
    st.sidebar.header("Database Status")
    st.sidebar.write(f"Networks: {len(summary_df)}")
    st.sidebar.write(f"Total Nodes: {len(nodes_df)}")
    st.sidebar.write(f"Total Edges: {len(edges_df)}")
    
    # Treatment pathway edges check
    treatment_edges_total = len(edges_df[edges_df['edge_type'] == 'leads_to_treatment'])
    st.sidebar.write(f"Treatment Connections: {treatment_edges_total}")
    
    # Choose exploration method
    st.header("How would you like to explore the research?")
    
    exploration_method = st.radio(
        "Choose your exploration method:",
        options=["Select by Grant (Funding Source)", "Select by Treatment (Research Outcome)"],
        index=0
    )
    
    st.markdown("---")
    
    # Show selection interface
    selected_network_id = None
    
    if exploration_method == "Select by Grant (Funding Source)":
        st.header("Select Research Grant")
        
        grant_options = {}
        for _, row in summary_df.iterrows():
            option_text = str(row['grant_id']) + " - " + str(row['disease']) + " Research"
            grant_options[option_text] = row['network_id']
        
        selected_grant = st.selectbox("Choose a research grant:", options=list(grant_options.keys()))
        
        if selected_grant:
            selected_network_id = grant_options[selected_grant]
            grant_info = summary_df[summary_df['network_id'] == selected_network_id].iloc[0]
            
            # Network info display
            st.markdown('<div class="network-info">', unsafe_allow_html=True)
            st.write("**Selected Grant:** " + str(grant_info['grant_id']))
            st.write("**Disease Area:** " + str(grant_info['disease']))
            st.write("**Funding Amount:** $" + "{:,.0f}".format(grant_info['funding_amount']))
            st.write("**Grant Year:** " + str(grant_info['grant_year']))
            st.write("**Resulting Treatment:** " + str(grant_info['treatment_name']))
            st.write("**FDA Approval:** " + str(grant_info['approval_year']))
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.header("Select Breakthrough Treatment")
        
        treatment_options = {}
        for _, row in summary_df.iterrows():
            option_text = str(row['treatment_name']) + " - " + str(row['disease'])
            treatment_options[option_text] = row['network_id']
        
        selected_treatment = st.selectbox("Choose a treatment:", options=list(treatment_options.keys()))
        
        if selected_treatment:
            selected_network_id = treatment_options[selected_treatment]
            treatment_info = summary_df[summary_df['network_id'] == selected_network_id].iloc[0]
            
            # Network info display
            st.markdown('<div class="network-info">', unsafe_allow_html=True)
            st.write("**Selected Treatment:** " + str(treatment_info['treatment_name']))
            st.write("**Disease Area:** " + str(treatment_info['disease']))
            st.write("**FDA Approval:** " + str(treatment_info['approval_year']))
            st.write("**Original Grant:** " + str(treatment_info['grant_id']))
            st.write("**Grant Funding:** $" + "{:,.0f}".format(treatment_info['funding_amount']))
            st.write("**Research Duration:** " + str(treatment_info['research_duration']) + " years")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Show network visualization
    if selected_network_id:
        st.markdown("---")
        st.header("Research Impact Network - WITH DEBUG")
        
        # Show the FIXED network with full debug
        fig = create_network_visualization(nodes_df, edges_df, selected_network_id)
        st.plotly_chart(fig, width='stretch')
        
        # Network analysis
        network_edges = edges_df[edges_df['network_id'] == selected_network_id]
        treatment_impact_edges = network_edges[network_edges['edge_type'] == 'leads_to_treatment']
        
        st.subheader("Network Analysis")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            grant_funding = len(network_edges[network_edges['edge_type'] == 'funded_by'])
            st.metric("Grant-Funded Papers", grant_funding)
        
        with col2:
            st.metric("Treatment Impact Citations", len(treatment_impact_edges))
        
        with col3:
            impact_percentage = (len(treatment_impact_edges) / grant_funding * 100) if grant_funding > 0 else 0
            st.metric("Impact Rate", f"{impact_percentage:.0f}%")
        
        # Key insights
        if len(treatment_impact_edges) > 0:
            st.success(f"✅ **SUCCESS**: Treatment development cited {len(treatment_impact_edges)} grant-funded publications!")
            st.info("""
            **Look for THICK ORANGE LINES connecting:**
            - **Orange circles (right)** = Treatment development papers
            - **Gray circles (left)** = Grant-funded research papers
            
            These orange lines prove the grant funding directly led to treatment development!
            """)
        else:
            st.error("❌ No treatment impact connections found")

if __name__ == "__main__":
    main()
