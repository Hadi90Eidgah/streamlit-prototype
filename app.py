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
    
    # Find papers that cite FT-funded papers (directly or indirectly)
    def find_papers_citing_ft(ft_papers, edges_df):
        citing_papers = set()
        
        # Direct citations
        for _, edge in edges_df.iterrows():
            if edge['edge_type'] == 'cites' and edge['target_id'] in ft_papers:
                citing_papers.add(edge['source_id'])
        
        # Indirect citations (papers that cite papers that cite FT papers)
        # This creates a broader network of FT influence
        previous_size = 0
        while len(citing_papers) > previous_size:
            previous_size = len(citing_papers)
            new_citing_papers = set()
            
            for _, edge in edges_df.iterrows():
                if edge['edge_type'] == 'cites' and edge['target_id'] in citing_papers:
                    new_citing_papers.add(edge['source_id'])
            
            citing_papers.update(new_citing_papers)
            
            # Prevent infinite loop
            if len(citing_papers) > 100:  # Safety limit
                break
        
        return citing_papers
    
    citing_ft_papers = find_papers_citing_ft(ft_funded_papers, edges_df)
    
    return ft_funded_papers, citing_ft_papers, approval_papers, treatment_nodes

def get_node_color(node_id, node_type, ft_funded, citing_ft, approval, treatment, distance):
    """Determine node color based on classification and distance"""
    base_colors = {
        'grant': '#1f77b4',  # Blue
        'ft_paper': '#1f77b4',  # Blue
        'citing_paper': '#ff7f0e',  # Orange
        'approval_paper': '#2ca02c',  # Green
        'treatment': '#2ca02c',  # Green
        'other_paper': '#808080'  # Darker grey (was #d3d3d3)
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
        intensity = 1 - (distance / max_distance) * 0.3  # 0.7 to 1.0 range
        intensity = max(0.7, min(1.0, intensity))
        
        # Convert hex to RGB and apply intensity
        hex_color = base_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        adjusted_rgb = tuple(int(c * intensity + 255 * (1 - intensity)) for c in rgb)
        return f'rgb({adjusted_rgb[0]}, {adjusted_rgb[1]}, {adjusted_rgb[2]})'
    
    return base_color

def create_hierarchical_layout(nodes_df, edges_df):
    """Create a hierarchical tree layout based on the logical flow"""
    # Create NetworkX graph
    G = nx.DiGraph()
    
    # Add nodes
    for _, node in nodes_df.iterrows():
        G.add_node(node['node_id'], **node.to_dict())
    
    # Add edges (reverse direction for proper hierarchy)
    for _, edge in edges_df.iterrows():
        if edge['edge_type'] == 'funded_by':
            G.add_edge(edge['source_id'], edge['target_id'])  # grant -> paper
        elif edge['edge_type'] == 'cites':
            G.add_edge(edge['target_id'], edge['source_id'])  # cited -> citing
        elif edge['edge_type'] == 'led_to_approval':
            G.add_edge(edge['source_id'], edge['target_id'])  # paper -> treatment
    
    # Find the grant node (root)
    grant_nodes = [node for node in G.nodes() if G.nodes[node]['node_type'] == 'grant']
    if not grant_nodes:
        # Fallback to spring layout if no grant found
        return nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    root = grant_nodes[0]
    
    # Calculate levels using BFS from the grant
    levels = {}
    queue = [(root, 0)]
    visited = {root}
    max_level = 0
    
    while queue:
        node, level = queue.pop(0)
        levels[node] = level
        max_level = max(max_level, level)
        
        # Add children to queue
        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, level + 1))
    
    # Assign positions based on levels
    pos = {}
    level_counts = {}
    level_positions = {}
    
    # Count nodes per level
    for node, level in levels.items():
        if level not in level_counts:
            level_counts[level] = 0
            level_positions[level] = 0
        level_counts[level] += 1
    
    # Position nodes
    for node, level in levels.items():
        x = level * 2.5  # Increased horizontal spacing
        
        # Vertical spacing within level
        total_in_level = level_counts[level]
        if total_in_level == 1:
            y = 0
        else:
            y_spacing = 4.0 / max(1, total_in_level - 1)  # Increased vertical spacing
            y = -2.0 + level_positions[level] * y_spacing
        
        pos[node] = (x, y)
        level_positions[level] += 1
    
    # Handle nodes not reached by BFS (disconnected components)
    for node in G.nodes():
        if node not in pos:
            pos[node] = (max_level + 2, 0)
    
    return pos

def create_network_graph(nodes_df, edges_df, show_edges=True):
    """Create an interactive network graph using Plotly"""
    # Create NetworkX graph for layout
    G = nx.DiGraph()
    
    # Add nodes
    for _, node in nodes_df.iterrows():
        G.add_node(node['node_id'], **node.to_dict())
    
    # Add edges (keep original direction for display)
    for _, edge in edges_df.iterrows():
        G.add_edge(edge['source_id'], edge['target_id'], **edge.to_dict())
    
    # Calculate hierarchical layout
    pos = create_hierarchical_layout(nodes_df, edges_df)
    
    # Classify nodes
    ft_funded, citing_ft, approval, treatment = classify_nodes(nodes_df, edges_df)
    
    # Prepare edge traces (only if show_edges is True)
    edge_traces = []
    if show_edges:
        edge_x = []
        edge_y = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create edge trace with better styling
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#cccccc'),  # Lighter, thinner edges
            hoverinfo='none',
            mode='lines',
            opacity=0.5,
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Prepare node traces
    node_x = []
    node_y = []
    node_colors = []
    node_sizes = []
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
            size = 30
        elif node_data['node_type'] == 'treatment':
            size = 35
        elif node_id in approval:
            size = 25
        elif node_id in ft_funded:
            size = 20
        else:
            size = 15
        node_sizes.append(size)
        
        # Hover information (detailed)
        hover_info = f"<b>{node_data['node_label']}</b><br>"
        hover_info += f"<b>Type:</b> {node_data['node_type'].replace('_', ' ').title()}<br>"
        
        if node_data['node_type'] == 'grant':
            hover_info += f"<b>Agency:</b> {details.get('agency', 'N/A')}<br>"
            hover_info += f"<b>Year:</b> {details.get('year', 'N/A')}<br>"
        elif node_data['node_type'] == 'treatment':
            hover_info += f"<b>Approval Agency:</b> {details.get('approval_agency', 'N/A')}<br>"
            hover_info += f"<b>Approval Year:</b> {details.get('approval_year', 'N/A')}<br>"
        else:
            if 'title' in details:
                title = details['title']
                if len(title) > 60:
                    title = title[:60] + "..."
                hover_info += f"<b>Title:</b> {title}<br>"
            if 'authors' in details:
                hover_info += f"<b>Authors:</b> {details['authors']}<br>"
            if 'year' in details:
                hover_info += f"<b>Year:</b> {details['year']}<br>"
            if 'journal' in details:
                journal = details['journal']
                if len(journal) > 40:
                    journal = journal[:40] + "..."
                hover_info += f"<b>Journal:</b> {journal}<br>"
            if distance >= 0:
                hover_info += f"<b>Distance to Approval:</b> {distance}<br>"
            if 'ft_grant' in details:
                hover_info += f"<b>Funded by:</b> Fondazione Telethon<br>"
        
        node_hover.append(hover_info)
    
    # Create node trace (no text labels by default)
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',  # Removed text mode
        hoverinfo='text',
        hovertext=node_hover,
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white'),
            opacity=0.9
        ),
        showlegend=False
    )
    
    # Create figure
    data = edge_traces + [node_trace] if show_edges else [node_trace]
    fig = go.Figure(data=data)
    
    # Update layout
    fig.update_layout(
        title='Research Grant to Treatment Lineage - Clean View',
        title_font_size=18,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=40,l=40,r=40,t=60),
        annotations=[dict(
            text="Grant (left) → FT Papers → Citations → Approval → Treatment (right). Hover for details.",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.5, y=-0.05,
            xanchor='center', yanchor='top',
            font=dict(color='#666', size=14)
        )],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white',
        height=600
    )
    
    return fig

def create_summary_table(nodes_df, edges_df):
    """Create a summary table of FT-funded publications"""
    ft_papers = []
    
    for _, node in nodes_df.iterrows():
        if node['node_type'] == 'paper':
            details = parse_node_details(node['details'])
            if 'ft_grant' in details:
                # Count how many times this paper is cited
                citation_count = len([e for _, e in edges_df.iterrows() 
                                    if e['edge_type'] == 'cites' and e['target_id'] == node['node_id']])
                
                ft_papers.append({
                    'Paper ID': node['node_id'],
                    'Title': details.get('title', 'N/A'),
                    'Authors': details.get('authors', 'N/A'),
                    'Year': details.get('year', 'N/A'),
                    'Journal': details.get('journal', 'N/A'),
                    'Citations': citation_count,
                    'Distance to Approval': details.get('node_distance_to_approval', 'N/A')
                })
    
    return pd.DataFrame(ft_papers)

def main():
    # Header
    st.markdown('<h1 class="main-header">🧬 Research Grant to Treatment Lineage</h1>', unsafe_allow_html=True)
    
    # Load data
    nodes_df, edges_df = load_data()
    
    # Sidebar with controls and information
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Toggle for showing edges
        show_edges = st.checkbox("Show Citation Edges", value=False, 
                                help="Toggle to show/hide the citation connections between papers")
        
        st.markdown("---")
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
        - 🟠 **Orange**: Papers citing FT research (direct/indirect)
        - 🟢 **Green**: Approval Paper & Treatment
        - ⚫ **Dark Grey**: Other Publications
        
        *Color intensity indicates distance to final approval*
        """)
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This visualization shows the realistic path from a Fondazione Telethon research grant 
        through scientific publications to the final approved treatment (Givinostat).
        
        **Key Features:**
        - Realistic citation patterns (not all FT papers are cited immediately)
        - Some FT papers may remain uncited
        - Cross-temporal citations (papers citing FT work years later)
        - Clean view with hover-only details
        """)
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📈 Citation Network Visualization")
        
        # Create and display the network graph
        fig = create_network_graph(nodes_df, edges_df, show_edges=show_edges)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📋 Quick Stats")
        
        # Calculate some interesting statistics
        ft_funded, citing_ft, approval, treatment = classify_nodes(nodes_df, edges_df)
        
        st.metric("FT-Funded Papers", len(ft_funded))
        st.metric("Papers Citing FT Research", len(citing_ft))
        st.metric("Approval Papers", len(approval))
        st.metric("Final Treatments", len(treatment))
        
        # Calculate citation statistics
        ft_paper_ids = [node['node_id'] for _, node in nodes_df.iterrows() 
                       if node['node_type'] == 'paper' and 'ft_grant' in parse_node_details(node['details'])]
        
        cited_ft_papers = set()
        for _, edge in edges_df.iterrows():
            if edge['edge_type'] == 'cites' and edge['target_id'] in ft_paper_ids:
                cited_ft_papers.add(edge['target_id'])
        
        uncited_ft_papers = len(ft_paper_ids) - len(cited_ft_papers)
        
        st.metric("Cited FT Papers", len(cited_ft_papers))
        st.metric("Uncited FT Papers", uncited_ft_papers)
        
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
        
        # Additional insights
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_citations = ft_table['Citations'].mean()
            st.metric("Avg Citations per FT Paper", f"{avg_citations:.1f}")
        with col2:
            most_cited = ft_table['Citations'].max()
            st.metric("Most Cited FT Paper", f"{most_cited} citations")
        with col3:
            uncited_count = len(ft_table[ft_table['Citations'] == 0])
            st.metric("Uncited FT Papers", uncited_count)
    else:
        st.info("No FT-funded publications found in the dataset.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9rem;'>
        <p>Exploring the Path from Research Grants to FDA and EMA Approved Treatments</p>
        <p>A Realistic Model of Research Impact and Citation Patterns</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
