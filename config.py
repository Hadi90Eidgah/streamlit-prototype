# Configuration for the Research Impact Dashboard

# --- Data Loading ---
DATABASE_PATH = 'streamlit_research_database.db'
NODES_CSV_PATH = 'streamlit_nodes.csv'
EDGES_CSV_PATH = 'streamlit_edges.csv'
SUMMARY_CSV_PATH = 'streamlit_summary.csv'
CACHE_TTL = 3600  # Cache data for 1 hour

# --- Node and Edge Types ---
NODE_TYPE_GRANT = 'grant'
NODE_TYPE_TREATMENT = 'treatment'
NODE_TYPE_PUBLICATION = 'publication'
EDGE_TYPE_FUNDED_BY = 'funded_by'
EDGE_TYPE_LEADS_TO_TREATMENT = 'leads_to_treatment'
EDGE_TYPE_CITES = 'cites'
EDGE_TYPE_ENABLES_TREATMENT = 'enables_treatment'

# --- Visualization ---
NODE_COLORS = {
    'grant': '#4299e1',
    'publication': '#a0aec0',
    'treatment': '#38b2ac',
    'grant_funded_pub': '#718096',
    'treatment_pathway_pub': '#ed8936',
    'ecosystem_pub': '#718096'
}

NODE_SIZES = {
    'grant': 30,
    'publication': 10,
    'treatment': 35,
    'grant_funded_pub': 12,
    'treatment_pathway_pub': 15,
    'ecosystem_pub': 8
}

EDGE_COLORS = {
    'funded_by': 'rgba(74, 85, 104, 0.8)',
    'leads_to_treatment': 'rgba(99, 179, 237, 0.9)',
    'cites': 'rgba(160, 174, 192, 0.25)',
    'enables_treatment': 'rgba(56, 178, 172, 0.8)'
}

EDGE_WIDTHS = {
    'funded_by': 3,
    'leads_to_treatment': 3,
    'cites': 0.8,
    'enables_treatment': 2
}

# --- Layout ---
NODE_POSITIONS_X = {
    'grant': -5,
    'grant_funded_pub': -2.5,
    'ecosystem_pub_cluster': [-0.5, 0.5, 1.5, 0],
    'treatment_pathway_pub': 3.5,
    'treatment': 6
}

NODE_POSITIONS_Y = {
    'grant': 0,
    'grant_funded_pub': [2, 0.7, -0.6, -1.9],
    'ecosystem_pub_cluster': [1, 0.5, -0.5, -1.5],
    'treatment_pathway_pub': [1, 0, -1],
    'treatment': 0
}

