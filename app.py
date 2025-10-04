import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Research Timeline: Grant to Treatment",
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
    .timeline-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
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
    ft_funded_papers = set()
    citing_ft_papers = set()
    approval_papers = set()
    treatment_nodes = set()
    
    # Find different node types
    for _, node in nodes_df.iterrows():
        details = parse_node_details(node['details'])
        
        if node['node_type'] == 'paper':
            if 'ft_grant' in details:
                ft_funded_papers.add(node['node_id'])
            elif details.get('is_approval_paper'):
                approval_papers.add(node['node_id'])
            elif details.get('cites_ft_papers'):
                citing_ft_papers.add(node['node_id'])
        elif node['node_type'] == 'treatment':
            treatment_nodes.add(node['node_id'])
    
    return ft_funded_papers, citing_ft_papers, approval_papers, treatment_nodes

def get_node_color_and_size(node_id, node_type, ft_funded, citing_ft, approval, treatment, details):
    """Determine node color and size based on classification"""
    
    # Color scheme
    colors = {
        'grant': '#1f77b4',      # Blue
        'ft_paper': '#1f77b4',   # Blue  
        'citing_paper': '#ff7f0e', # Orange
        'approval_paper': '#2ca02c', # Green
        'treatment': '#2ca02c',   # Green
        'other_paper': '#808080'  # Dark grey
    }
    
    # Size scheme
    sizes = {
        'grant': 35,
        'ft_paper': 25,
        'citing_paper': 20,
        'approval_paper': 30,
        'treatment': 40,
        'other_paper': 15
    }
    
    # Determine category
    if node_type == 'grant':
        category = 'grant'
    elif node_id in treatment:
        category = 'treatment'
    elif node_id in approval:
        category = 'approval_paper'
    elif node_id in ft_funded:
        category = 'ft_paper'
    elif node_id in citing_ft:
        category = 'citing_paper'
    else:
        category = 'other_paper'
    
    return colors[category], sizes[category]

def create_timeline_visualization(nodes_df, edges_df, show_edges=True):
    """Create timeline-based visualization with Y-axis as years"""
    
    # Classify nodes
    ft_funded, citing_ft, approval, treatment = classify_nodes(nodes_df, edges_df)
    
    # Prepare data for plotting
    node_data = []
    
    for _, node in nodes_df.iterrows():
        details = parse_node_details(node['details'])
        
        # Get position data
        year = details.get('year', 2020)  # Default year if missing
        x_pos = details.get('x_position', 0)  # Default center if missing
        
        # Get color and size
        color, size = get_node_color_and_size(
            node['node_id'], node['node_type'], 
            ft_funded, citing_ft, approval, treatment, details
        )
        
        # Create hover text
        hover_text = f"<b>{node['node_label']}</b><br>"
        
        if node['node_type'] == 'grant':
            hover_text += f"<b>Type:</b> Research Grant<br>"
            hover_text += f"<b>Agency:</b> {details.get('agency', 'N/A')}<br>"
            hover_text += f"<b>Year:</b> {year}<br>"
            hover_text += f"<b>Title:</b> {details.get('grant_title', 'N/A')}<br>"
            
        elif node['node_type'] == 'treatment':
            hover_text += f"<b>Type:</b> Approved Treatment<br>"
            hover_text += f"<b>Name:</b> {details.get('treatment_name', 'N/A')}<br>"
            hover_text += f"<b>Approval Year:</b> {year}<br>"
            hover_text += f"<b>Agency:</b> {details.get('approval_agency', 'N/A')}<br>"
            hover_text += f"<b>Indication:</b> {details.get('indication', 'N/A')}<br>"
            
        else:  # Paper
            hover_text += f"<b>Type:</b> Research Paper<br>"
            hover_text += f"<b>PubMed ID:</b> {node['node_label']}<br>"
            hover_text += f"<b>Year:</b> {year}<br>"
            
            title = details.get('title', 'N/A')
            if len(title) > 60:
                title = title[:60] + "..."
            hover_text += f"<b>Title:</b> {title}<br>"
            
            hover_text += f"<b>Authors:</b> {details.get('authors', 'N/A')}<br>"
            hover_text += f"<b>Journal:</b> {details.get('journal', 'N/A')}<br>"
            
            # Special annotations for FT-related papers
            if 'ft_grant' in details:
                hover_text += f"<b>Funding:</b> Fondazione Telethon<br>"
            
            if details.get('cites_ft_papers'):
                cited_papers = details['cites_ft_papers']
                hover_text += f"<b>Cites FT Papers:</b> {len(cited_papers)} paper(s)<br>"
                for ft_paper in cited_papers[:2]:  # Show first 2
                    hover_text += f"  • {ft_paper}<br>"
                if len(cited_papers) > 2:
                    hover_text += f"  • ... and {len(cited_papers) - 2} more<br>"
            
            distance = details.get('node_distance_to_approval', -1)
            if distance >= 0:
                hover_text += f"<b>Distance to Approval:</b> {distance} steps<br>"
        
        node_data.append({
            'node_id': node['node_id'],
            'x': x_pos,
            'y': year,
            'color': color,
            'size': size,
            'hover_text': hover_text,
            'node_type': node['node_type']
        })
    
    # Create the plot
    fig = go.Figure()
    
    # Add edges if requested
    if show_edges:
        edge_x = []
        edge_y = []
        
        # Create position lookup
        pos_lookup = {item['node_id']: (item['x'], item['y']) for item in node_data}
        
        for _, edge in edges_df.iterrows():
            if edge['source_id'] in pos_lookup and edge['target_id'] in pos_lookup:
                x0, y0 = pos_lookup[edge['source_id']]
                x1, y1 = pos_lookup[edge['target_id']]
                
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        # Add edge trace
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=1, color='rgba(128,128,128,0.3)'),
            hoverinfo='none',
            showlegend=False,
            name='Citations'
        ))
    
    # Group nodes by type for better legend
    node_types = ['grant', 'paper', 'treatment']
    type_names = {'grant': 'Grant', 'paper': 'Papers', 'treatment': 'Treatment'}
    
    for node_type in node_types:
        type_data = [item for item in node_data if item['node_type'] == node_type]
        
        if type_data:
            fig.add_trace(go.Scatter(
                x=[item['x'] for item in type_data],
                y=[item['y'] for item in type_data],
                mode='markers',
                marker=dict(
                    size=[item['size'] for item in type_data],
                    color=[item['color'] for item in type_data],
                    line=dict(width=2, color='white'),
                    opacity=0.9
                ),
                text=[item['hover_text'] for item in type_data],
                hoverinfo='text',
                name=type_names[node_type],
                showlegend=False
            ))
    
    # Update layout for timeline view
    fig.update_layout(
        title={
            'text': 'Research Timeline: From Grant to Treatment',
            'x': 0.5,
            'font': {'size': 20}
        },
        xaxis=dict(
            title='Research Branches',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(128,128,128,0.4)',
            showticklabels=False
        ),
        yaxis=dict(
            title='Year',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            tickmode='linear',
            dtick=1,
            range=[2009, 2025]
        ),
        hovermode='closest',
        plot_bgcolor='white',
        height=700,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # Add year annotations for key events
    key_years = [
        (2010, "Grant Awarded"),
        (2024, "Treatment Approved")
    ]
    
    annotations = []
    for year, label in key_years:
        annotations.append(dict(
            x=-8,  # Left side
            y=year,
            text=f"<b>{label}</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='#666',
            ax=-40,
            ay=0,
            font=dict(size=12, color='#666'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#666',
            borderwidth=1
        ))
    
    fig.update_layout(annotations=annotations)
    
    return fig

def create_summary_statistics(nodes_df, edges_df):
    """Create summary statistics for the timeline"""
    ft_funded, citing_ft, approval, treatment = classify_nodes(nodes_df, edges_df)
    
    # Calculate timeline span
    years = []
    for _, node in nodes_df.iterrows():
        details = parse_node_details(node['details'])
        if 'year' in details:
            years.append(details['year'])
    
    timeline_span = max(years) - min(years) if years else 0
    
    # Count FT citations
    ft_citations = 0
    papers_citing_ft = 0
    
    for _, node in nodes_df.iterrows():
        if node['node_type'] == 'paper':
            details = parse_node_details(node['details'])
            if details.get('cites_ft_papers'):
                papers_citing_ft += 1
                ft_citations += len(details['cites_ft_papers'])
    
    return {
        'timeline_span': timeline_span,
        'total_papers': len(nodes_df[nodes_df['node_type'] == 'paper']),
        'ft_funded_papers': len(ft_funded),
        'papers_citing_ft': papers_citing_ft,
        'total_ft_citations': ft_citations,
        'approval_papers': len(approval)
    }

def main():
    # Header
    st.markdown('<h1 class="main-header">🧬 Research Timeline: Grant to Treatment</h1>', unsafe_allow_html=True)
    
    # Load data
    nodes_df, edges_df = load_data()
    
    # Sidebar with controls and information
    with st.sidebar:
        st.header("🎛️ Visualization Controls")
        
        # Toggle for showing edges
        show_edges = st.checkbox("Show Citation Connections", value=False, 
                                help="Toggle to show/hide the citation lines between papers")
        
        st.markdown("---")
        st.header("📊 Timeline Statistics")
        
        stats = create_summary_statistics(nodes_df, edges_df)
        
        st.metric("Timeline Span", f"{stats['timeline_span']} years")
        st.metric("Total Papers", stats['total_papers'])
        st.metric("FT-Funded Papers", stats['ft_funded_papers'])
        st.metric("Papers Citing FT Research", stats['papers_citing_ft'])
        st.metric("Total FT Citations", stats['total_ft_citations'])
        st.metric("Approval Papers", stats['approval_papers'])
        
        st.markdown("---")
        st.header("🎨 Color Legend")
        st.markdown("""
        - 🔵 **Blue**: Grant & FT-Funded Papers
        - 🟠 **Orange**: Papers Citing FT Research  
        - 🟢 **Green**: Approval Papers & Treatment
        - ⚫ **Dark Grey**: Other Papers
        
        *Node size indicates importance in the research timeline*
        """)
        
        st.markdown("---")
        st.header("📅 Timeline Concept")
        st.markdown("""
        **Y-Axis = Years**: Each node is positioned by its publication/approval year
        
        **X-Axis = Research Branches**: Papers are spread horizontally to show different research paths
        
        **Hover for Details**: PubMed IDs, titles, and FT citation information
        """)
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This timeline visualization shows the realistic 14-year journey from a Fondazione Telethon research grant (2010) to the approved treatment Givinostat (2024).
        
        The visualization clearly shows:
        - When each research milestone occurred
        - Which papers cite FT-funded research
        - The citation network leading to approval
        """)
    
    # Main visualization
    st.subheader("📈 Research Timeline Visualization")
    
    # Create timeline info box
    st.markdown("""
    <div class="timeline-info">
        <strong>📅 Timeline Overview:</strong> This visualization shows the 14-year research journey from grant (2010) to treatment approval (2024). 
        The Y-axis represents years, and the X-axis shows different research branches. 
        Hover over any node to see detailed information including PubMed IDs and FT citations.
    </div>
    """, unsafe_allow_html=True)
    
    # Create and display the timeline visualization
    fig = create_timeline_visualization(nodes_df, edges_df, show_edges=show_edges)
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional insights
    st.markdown("---")
    st.subheader("🔍 Key Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Research Impact")
        stats = create_summary_statistics(nodes_df, edges_df)
        impact_rate = (stats['papers_citing_ft'] / stats['total_papers']) * 100 if stats['total_papers'] > 0 else 0
        st.metric("FT Research Impact", f"{impact_rate:.1f}%", 
                 help="Percentage of papers that cite FT-funded research")
    
    with col2:
        st.markdown("### ⏱️ Research Timeline")
        st.metric("Grant to Approval", "14 years", 
                 help="Time from initial grant to treatment approval")
        
    with col3:
        st.markdown("### 🎯 Citation Network")
        avg_citations = stats['total_ft_citations'] / stats['ft_funded_papers'] if stats['ft_funded_papers'] > 0 else 0
        st.metric("Avg Citations per FT Paper", f"{avg_citations:.1f}",
                 help="Average number of times each FT paper is cited")
    
    # FT Papers detailed table
    st.markdown("---")
    st.subheader("📚 Fondazione Telethon Funded Papers")
    
    ft_papers_data = []
    for _, node in nodes_df.iterrows():
        if node['node_type'] == 'paper':
            details = parse_node_details(node['details'])
            if 'ft_grant' in details:
                # Count citations
                citation_count = len([e for _, e in edges_df.iterrows() 
                                    if e['edge_type'] == 'cites' and e['target_id'] == node['node_id']])
                
                ft_papers_data.append({
                    'PubMed ID': node['node_label'],
                    'Title': details.get('title', 'N/A'),
                    'Year': details.get('year', 'N/A'),
                    'Journal': details.get('journal', 'N/A'),
                    'Citations Received': citation_count,
                    'Distance to Approval': details.get('node_distance_to_approval', 'N/A')
                })
    
    if ft_papers_data:
        ft_df = pd.DataFrame(ft_papers_data)
        st.dataframe(ft_df, use_container_width=True)
    else:
        st.info("No FT-funded papers found in the dataset.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9rem;'>
        <p><strong>Timeline-Based Research Impact Visualization</strong></p>
        <p>Tracking the Journey from Fondazione Telethon Grant to FDA/EMA Approved Treatment</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
