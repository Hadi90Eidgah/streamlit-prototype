"""
Research Impact Dashboard - Final Version
Beautiful network visualization matching Drawing.pdf style
Perfect for stakeholder presentations and fundraising demonstrations
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
        
        # Position grant (large blue circle) on the left
        if len(grants) > 0:
            grant_node = grants.iloc[0]
            node_positions[grant_node['node_id']] = (-4, 0)
        
        # Position initial publications (gray circles) connected to grant
        initial_pubs = publications.head(4) if len(publications) >= 4 else publications
        for i, (_, pub) in enumerate(initial_pubs.iterrows()):
            y_pos = 1.5 - (i * 1.0)
            node_positions[pub['node_id']] = (-2, y_pos)
        
        # Position research ecosystem (white circles) in organized clusters
        research_pubs = publications.iloc[4:] if len(publications) > 4 else pd.DataFrame()
        np.random.seed(42)
        
        for i, (_, pub) in enumerate(research_pubs.iterrows()):
            x_pos = np.random.uniform(-1, 3)
            y_pos = np.random.uniform(-2, 2)
            node_positions[pub['node_id']] = (x_pos, y_pos)
        
        # Position treatment pathway nodes (yellow circles)
        treatment_pubs = publications.tail(3) if len(publications) >= 3 else publications.tail(len(publications))
        for i, (_, pub) in enumerate(treatment_pubs.iterrows()):
            y_pos = 0.8 - (i * 0.8)
            node_positions[pub['node_id']] = (4, y_pos)
        
        # Position treatment (large green circle) on the right
        if len(treatments) > 0:
            treatment_node = treatments.iloc[0]
            node_positions[treatment_node['node_id']] = (6, 0)
        
        # Create clean edges
        edge_x = []
        edge_y = []
        
        for _, edge in network_edges.iterrows():
            if edge['source_id'] in node_positions and edge['target_id'] in node_positions:
                x0, y0 = node_positions[edge['source_id']]
                x1, y1 = node_positions[edge['target_id']]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888', dash='solid'),
            hoverinfo='none',
            mode='lines',
            showlegend=False,
            opacity=0.6
        )
        
        # Create node traces with elegant styling
        node_traces = []
        colors = {'grant': '#1f4e79', 'publication': '#d1d5db', 'treatment': '#059669'}
        sizes = {'grant': 40, 'publication': 12, 'treatment': 35}
        
        # Identify treatment pathway nodes for special styling
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
                            node_colors.append('#fbbf24')  # Yellow
                            node_sizes.append(18)
                            text = "🟡 KEY RESEARCH<br>Treatment Pathway"
                        else:
                            node_colors.append(colors[node_type])
                            node_sizes.append(sizes[node_type])
                            
                            if node_type == 'grant':
                                text = "🔵 RESEARCH GRANT<br>Funding Source"
                            elif node_type == 'treatment':
                                text = "🟢 BREAKTHROUGH TREATMENT<br>FDA Approved"
                            else:
                                text = "⚪ RESEARCH PUBLICATION<br>Supporting Evidence"
                        
                        node_text.append(text)
                
                if node_x:
                    # Group nodes by color for clean legend
                    unique_colors = list(set(node_colors))
                    
                    for color in unique_colors:
                        color_indices = [i for i, c in enumerate(node_colors) if c == color]
                        
                        if color_indices:
                            trace_x = [node_x[i] for i in color_indices]
                            trace_y = [node_y[i] for i in color_indices]
                            trace_text = [node_text[i] for i in color_indices]
                            trace_sizes = [node_sizes[i] for i in color_indices]
                            
                            # Determine trace name for legend
                            if color == '#fbbf24':
                                trace_name = "🟡 Treatment Pathway"
                            elif node_type == 'grant':
                                trace_name = "🔵 Research Grant"
                            elif node_type == 'treatment':
                                trace_name = "🟢 Breakthrough Treatment"
                            else:
                                trace_name = "⚪ Research Publications"
                            
                            node_trace = go.Scatter(
                                x=trace_x, y=trace_y,
                                mode='markers',
                                hoverinfo='text',
                                text=trace_text,
                                marker=dict(
                                    size=trace_sizes,
                                    color=color,
                                    line=dict(width=2, color='white'),
                                    opacity=0.9
                                ),
                                name=trace_name,
                                showlegend=True
                            )
                            node_traces.append(node_trace)
        
        # Create elegant figure
        fig = go.Figure(data=[edge_trace] + node_traces)
        
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
        st.error("Error creating network: " + str(e))
        return go.Figure()

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔬 Research Impact Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Explore Research Networks by Grant or Treatment</p>', unsafe_allow_html=True)
    
    # Load data
    nodes_df, edges_df, summary_df = load_database()
    
    # Choose exploration method
    st.header("🎯 How would you like to explore the research?")
    
    exploration_method = st.radio(
        "Choose your exploration method:",
        options=["Select by Grant (Funding Source)", "Select by Treatment (Research Outcome)"],
        index=0,
        help="Choose whether to start from the funding source or the final treatment outcome"
    )
    
    st.markdown("---")
    
    # Show selection interface
    selected_network_id = None
    
    if exploration_method == "Select by Grant (Funding Source)":
        st.header("📋 Select Research Grant")
        st.write("Choose a research grant to see how funding led to breakthrough treatments:")
        
        grant_options = {}
        for _, row in summary_df.iterrows():
            option_text = str(row['grant_id']) + " - " + str(row['disease']) + " Research"
            grant_options[option_text] = row['network_id']
        
        selected_grant = st.selectbox(
            "Choose a research grant:",
            options=list(grant_options.keys()),
            key="grant_selector"
        )
        
        if selected_grant:
            selected_network_id = grant_options[selected_grant]
            grant_info = summary_df[summary_df['network_id'] == selected_network_id].iloc[0]
            
            grant_card = '<div class="selection-card grant-card">'
            grant_card += '<h3>📋 ' + str(grant_info['grant_id']) + '</h3>'
            grant_card += '<p><strong>Disease Focus:</strong> ' + str(grant_info['disease']) + '</p>'
            grant_card += '<p><strong>Funding Amount:</strong> $' + "{:,.0f}".format(grant_info['funding_amount']) + '</p>'
            grant_card += '<p><strong>Grant Year:</strong> ' + str(grant_info['grant_year']) + '</p>'
            grant_card += '<p><strong>Research Duration:</strong> ' + str(grant_info['research_duration']) + ' years</p>'
            grant_card += '<p class="success-metric">✅ Led to FDA-approved treatment: ' + str(grant_info['treatment_name']) + '</p>'
            grant_card += '</div>'
            
            st.markdown(grant_card, unsafe_allow_html=True)
    
    else:
        st.header("🎯 Select Breakthrough Treatment")
        st.write("Choose a breakthrough treatment to see the research pathway that led to its development:")
        
        treatment_options = {}
        for _, row in summary_df.iterrows():
            option_text = str(row['treatment_name']) + " - " + str(row['disease']) + " Treatment"
            treatment_options[option_text] = row['network_id']
        
        selected_treatment = st.selectbox(
            "Choose a breakthrough treatment:",
            options=list(treatment_options.keys()),
            key="treatment_selector"
        )
        
        if selected_treatment:
            selected_network_id = treatment_options[selected_treatment]
            treatment_info = summary_df[summary_df['network_id'] == selected_network_id].iloc[0]
            
            treatment_card = '<div class="selection-card treatment-card">'
            treatment_card += '<h3>🎯 ' + str(treatment_info['treatment_name']) + '</h3>'
            treatment_card += '<p><strong>Disease Treated:</strong> ' + str(treatment_info['disease']) + '</p>'
            treatment_card += '<p><strong>FDA Approval Year:</strong> ' + str(treatment_info['approval_year']) + '</p>'
            treatment_card += '<p><strong>Research Publications:</strong> ' + str(treatment_info['total_publications']) + ' papers</p>'
            treatment_card += '<p><strong>Development Time:</strong> ' + str(treatment_info['research_duration']) + ' years</p>'
            treatment_card += '<p class="success-metric">💰 Original Grant: ' + str(treatment_info['grant_id']) + ' ($' + "{:,.0f}".format(treatment_info['funding_amount']) + ')</p>'
            treatment_card += '</div>'
            
            st.markdown(treatment_card, unsafe_allow_html=True)
    
    # Show elegant network if selection is made
    if selected_network_id:
        st.markdown("---")
        
        network_info = summary_df[summary_df['network_id'] == selected_network_id].iloc[0]
        
        st.header("🕸️ Research Impact Network: " + str(network_info['disease']))
        
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
            st.metric("Duration", str(network_info['research_duration']) + " years")
        
        # Show elegant network
        st.subheader("📊 Research Impact Network")
        
        fig = create_elegant_network(nodes_df, edges_df, selected_network_id)
        st.plotly_chart(fig, width='stretch')
        
        # Network explanation
        explanation = "**How to read this network:**\n"
        explanation += "- 🔵 **Blue circle** = Research grant (funding source)\n"
        explanation += "- ⚪ **Gray circles** = Research publications\n"
        explanation += "- 🟡 **Yellow circles** = Key research leading to treatment\n"
        explanation += "- 🟢 **Green circle** = Breakthrough treatment (FDA approved)\n"
        explanation += "- **Lines** show research connections and funding flow"
        
        st.info(explanation)
        
        # Research impact summary
        st.subheader("📈 Complete Research Impact Story")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔬 Research Journey:**")
            st.write("**Grant:** " + str(network_info['grant_id']) + " (" + str(network_info['grant_year']) + ")")
            st.write("**Funding:** $" + "{:,.0f}".format(network_info['funding_amount']))
            st.write("**Publications:** " + str(network_info['total_publications']) + " research papers")
            st.write("**Research Duration:** " + str(network_info['research_duration']) + " years")
        
        with col2:
            st.markdown("**🎯 Breakthrough Outcome:**")
            st.write("**Treatment:** " + str(network_info['treatment_name']))
            st.write("**Disease:** " + str(network_info['disease']))
            st.write("**FDA Approval:** " + str(network_info['approval_year']))
            st.write("**Status:** ✅ Successfully Approved")
        
        # ROI calculation
        cost_per_pub = network_info['funding_amount'] / network_info['total_publications']
        roi_text = "This $" + "{:,.0f}".format(network_info['funding_amount']) + " grant "
        roi_text += "generated " + str(network_info['total_publications']) + " publications "
        roi_text += "($" + "{:,.0f}".format(cost_per_pub) + " per publication) "
        roi_text += "and led to FDA approval in " + str(network_info['research_duration']) + " years."
        
        st.success("💰 **Return on Investment:** " + roi_text)
        
        # Call to action
        st.markdown("---")
        cta_text = "**🎯 This demonstrates how institutional funding directly creates breakthrough treatments!**"
        st.markdown('<p style="text-align: center; font-size: 1.3rem; color: #28a745; font-weight: bold;">' + cta_text + '</p>', unsafe_allow_html=True)
    
    else:
        # Show overall summary
        st.markdown("---")
        st.header("📊 Overall Research Impact")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_funding = summary_df['funding_amount'].sum()
            st.metric("Total Investment", "$" + "{:,.0f}".format(total_funding))
        
        with col2:
            total_pubs = summary_df['total_publications'].sum()
            st.metric("Total Publications", "{:,}".format(total_pubs))
        
        with col3:
            st.metric("Success Rate", "100%", help="All grants led to approved treatments")
        
        st.info("👆 **Choose your exploration method above, then select a specific grant or treatment to see the elegant research network.**")

if __name__ == "__main__":
    main()
