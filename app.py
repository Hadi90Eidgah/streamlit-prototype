"""
Research Impact Dashboard - Streamlit App (SIMPLE VERSION)
Reads all files from repository root (no data folder needed)
Demonstrates how institutional funding leads to breakthrough treatments
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
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
        # Try SQLite first (in root directory)
        if os.path.exists('streamlit_research_database.db'):
            conn = sqlite3.connect('streamlit_research_database.db')
            nodes_df = pd.read_sql('SELECT * FROM nodes', conn)
            edges_df = pd.read_sql('SELECT * FROM edges', conn)
            summary_df = pd.read_sql('SELECT * FROM network_summary', conn)
            conn.close()
            st.success("✅ Loaded data from SQLite database")
            return nodes_df, edges_df, summary_df
        else:
            st.info("SQLite database not found, trying CSV files...")
    except Exception as e:
        st.warning(f"SQLite error: {e}")
    
    try:
        # Try CSV files (in root directory)
        nodes_df = pd.read_csv('streamlit_nodes.csv')
        edges_df = pd.read_csv('streamlit_edges.csv')
        summary_df = pd.read_csv('streamlit_summary.csv')
        st.success("✅ Loaded data from CSV files")
        return nodes_df, edges_df, summary_df
    except Exception as e:
        st.warning(f"CSV error: {e}")
    
    # If all else fails, create sample data
    st.info("📊 Using sample data for demonstration")
    return create_sample_data()

def create_sample_data():
    """Create sample data if files are not available"""
    
    # Sample summary data
    summary_df = pd.DataFrame({
        'network_id': [1, 2, 3],
        'disease': ['Cancer', 'Alzheimer\'s Disease', 'Diabetes'],
        'treatment_name': ['CAR-T Cell Therapy', 'Aducanumab Plus', 'Smart Insulin Patch'],
        'grant_id': ['INST-R01-877572', 'INST-U01-352422', 'INST-U01-448787'],
        'grant_year': [2015, 2019, 2015],
        'approval_year': [2024, 2023, 2025],
        'funding_amount': [2807113, 2304762, 1983309],
        'total_publications': [37, 37, 37],
        'research_duration': [9, 4, 10],
        'color': ['#FF6B6B', '#4ECDC4', '#45B7D1']
    })
    
    # Sample nodes data
    nodes_df = pd.DataFrame({
        'node_id': ['GRANT_1', 'GRANT_2', 'GRANT_3', 'TREAT_1', 'TREAT_2', 'TREAT_3'],
        'node_type': ['grant', 'grant', 'grant', 'treatment', 'treatment', 'treatment'],
        'network_id': [1, 2, 3, 1, 2, 3],
        'funding_amount': [2807113, 2304762, 1983309, None, None, None],
        'treatment_name': [None, None, None, 'CAR-T Cell Therapy', 'Aducanumab Plus', 'Smart Insulin Patch']
    })
    
    # Sample edges data
    edges_df = pd.DataFrame({
        'source_id': ['GRANT_1', 'GRANT_2', 'GRANT_3'],
        'target_id': ['TREAT_1', 'TREAT_2', 'TREAT_3'],
        'edge_type': ['leads_to', 'leads_to', 'leads_to'],
        'network_id': [1, 2, 3]
    })
    
    return nodes_df, edges_df, summary_df

@st.cache_data
def calculate_roi_metrics(summary_df, nodes_df):
    """Calculate ROI and impact metrics"""
    total_funding = summary_df['funding_amount'].sum()
    total_publications = summary_df['total_publications'].sum() if 'total_publications' in summary_df.columns else 111
    total_treatments = len(summary_df)
    
    # Calculate metrics
    cost_per_publication = total_funding / total_publications if total_publications > 0 else 0
    cost_per_treatment = total_funding / total_treatments if total_treatments > 0 else 0
    avg_research_duration = summary_df['research_duration'].mean() if 'research_duration' in summary_df.columns else 7.7
    
    return {
        'total_funding': total_funding,
        'total_publications': total_publications,
        'total_treatments': total_treatments,
        'cost_per_publication': cost_per_publication,
        'cost_per_treatment': cost_per_treatment,
        'avg_research_duration': avg_research_duration,
        'success_rate': (total_treatments / len(summary_df)) * 100
    }

def create_timeline_chart(summary_df):
    """Create timeline visualization"""
    try:
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
    
    except Exception as e:
        st.error(f"Error creating timeline chart: {e}")
        return go.Figure()

def create_simple_network_chart(summary_df):
    """Create a simple network visualization using summary data"""
    try:
        fig = go.Figure()
        
        # Create a simple flow chart showing grant -> treatment
        for i, network in summary_df.iterrows():
            y_pos = len(summary_df) - i
            
            # Grant node
            fig.add_trace(go.Scatter(
                x=[1],
                y=[y_pos],
                mode='markers+text',
                marker=dict(size=30, color='blue'),
                text=[f"Grant<br>${network['funding_amount']/1000000:.1f}M"],
                textposition="middle center",
                textfont=dict(color="white", size=10),
                name=f"{network['disease']} Grant",
                showlegend=False,
                hovertemplate=f"<b>Grant: {network['grant_id']}</b><br>Funding: ${network['funding_amount']:,.0f}<br>Year: {network['grant_year']}<extra></extra>"
            ))
            
            # Arrow
            fig.add_annotation(
                x=1.5, y=y_pos,
                ax=1.3, ay=y_pos,
                xref='x', yref='y',
                axref='x', ayref='y',
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='gray'
            )
            
            # Treatment node
            fig.add_trace(go.Scatter(
                x=[2],
                y=[y_pos],
                mode='markers+text',
                marker=dict(size=30, color='green'),
                text=[f"Treatment<br>{network['research_duration']}yr"],
                textposition="middle center",
                textfont=dict(color="white", size=10),
                name=f"{network['disease']} Treatment",
                showlegend=False,
                hovertemplate=f"<b>Treatment: {network['treatment_name']}</b><br>Approved: {network['approval_year']}<br>Duration: {network['research_duration']} years<extra></extra>"
            ))
            
            # Disease label
            fig.add_annotation(
                x=0.5, y=y_pos,
                text=f"<b>{network['disease']}</b>",
                showarrow=False,
                font=dict(size=12)
            )
        
        fig.update_layout(
            title="Research Impact Flow: Grant → Treatment",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 2.5]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=300,
            hovermode='closest'
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating network chart: {e}")
        return go.Figure()

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔬 Research Impact Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Demonstrating How Institutional Funding Creates Breakthrough Treatments</p>', unsafe_allow_html=True)
    
    # Load data
    nodes_df, edges_df, summary_df = load_database()
    roi_metrics = calculate_roi_metrics(summary_df, nodes_df)
    
    # Sidebar
    st.sidebar.title("🎯 Dashboard Controls")
    
    # Show/hide sections
    show_overview = st.sidebar.checkbox("📊 Overview Metrics", value=True)
    show_networks = st.sidebar.checkbox("🔬 Network Details", value=True)
    show_timeline = st.sidebar.checkbox("📅 Research Timeline", value=True)
    show_flow = st.sidebar.checkbox("🔄 Research Flow", value=True)
    
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
        st.plotly_chart(timeline_fig, width='stretch')
    
    # Research Flow Visualization
    if show_flow:
        st.header("🔄 Research Impact Flow")
        flow_fig = create_simple_network_chart(summary_df)
        st.plotly_chart(flow_fig, width='stretch')
    
    # Summary Table
    st.header("📋 Research Networks Summary")
    
    # Create a nice summary table
    display_df = summary_df.copy()
    display_df['Funding'] = display_df['funding_amount'].apply(lambda x: f"${x:,.0f}")
    display_df['Duration'] = display_df['research_duration'].apply(lambda x: f"{x} years")
    display_df['Grant Period'] = display_df['grant_year'].astype(str) + " - " + display_df['approval_year'].astype(str)
    
    summary_table = display_df[['disease', 'treatment_name', 'grant_id', 'Funding', 'Duration', 'total_publications', 'Grant Period']]
    summary_table.columns = ['Disease', 'Treatment', 'Grant ID', 'Funding', 'Duration', 'Publications', 'Period']
    
    st.dataframe(summary_table, width=800)
    
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
