"""
Manual Database Update Script
Updates specific networks with new treatments and diseases
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime

def update_database_manually():
    """Update database with new treatments and diseases"""
    
    print("🔧 Starting Manual Database Update...")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect('streamlit_research_database.db')
    
    # Read current data
    nodes_df = pd.read_sql('SELECT * FROM nodes', conn)
    edges_df = pd.read_sql('SELECT * FROM edges', conn)
    summary_df = pd.read_sql('SELECT * FROM network_summary', conn)
    
    print(f"📊 Current Database:")
    print(f"   Nodes: {len(nodes_df)}")
    print(f"   Edges: {len(edges_df)}")
    print(f"   Networks: {len(summary_df)}")
    
    # Network modifications
    network_updates = {
        1: {
            "disease": "Duchenne Muscular Dystrophy",
            "treatment_name": "Givinostat",
            "grant_focus": "Neuromuscular Disease Research",
            "keywords": ["duchenne", "muscular dystrophy", "histone deacetylase", "HDAC", "muscle"],
            "approval_year": 2024
        },
        2: {
            "disease": "Huntington's Disease",
            "treatment_name": "AMT-130",
            "grant_focus": "Neurodegenerative Disease Research", 
            "keywords": ["huntington", "gene therapy", "AAV", "huntingtin", "neurodegeneration"],
            "approval_year": 2025
        }
        # Network 3 (Diabetes) remains unchanged
    }
    
    print(f"\\n🎯 Planned Updates:")
    for net_id, updates in network_updates.items():
        print(f"   Network {net_id}: {updates['disease']} → {updates['treatment_name']}")
    
    # Update nodes
    print(f"\\n📝 Updating Nodes...")
    
    for net_id, updates in network_updates.items():
        # Update grant nodes
        grant_mask = (nodes_df['network_id'] == net_id) & (nodes_df['node_type'] == 'grant')
        if grant_mask.any():
            nodes_df.loc[grant_mask, 'disease'] = updates['disease']
            nodes_df.loc[grant_mask, 'treatment_name'] = updates['treatment_name']
            nodes_df.loc[grant_mask, 'approval_year'] = updates['approval_year']
            nodes_df.loc[grant_mask, 'title'] = f"{updates['grant_focus']} Initiative"
            print(f"   ✅ Updated grant node for Network {net_id}")
        
        # Update treatment nodes
        treatment_mask = (nodes_df['network_id'] == net_id) & (nodes_df['node_type'] == 'treatment')
        if treatment_mask.any():
            nodes_df.loc[treatment_mask, 'treatment_name'] = updates['treatment_name']
            nodes_df.loc[treatment_mask, 'disease'] = updates['disease']
            nodes_df.loc[treatment_mask, 'approval_year'] = updates['approval_year']
            print(f"   ✅ Updated treatment node for Network {net_id}")
        
        # Update publication titles to reflect new disease/treatment
        pub_mask = (nodes_df['network_id'] == net_id) & (nodes_df['node_type'] == 'publication')
        if pub_mask.any():
            # Update titles for grant-funded publications
            grant_pub_mask = pub_mask & (nodes_df['node_id'].str.startswith('PUB_'))
            if grant_pub_mask.any():
                nodes_df.loc[grant_pub_mask, 'title'] = nodes_df.loc[grant_pub_mask, 'title'].apply(
                    lambda x: f"Molecular mechanisms of {updates['keywords'][0]} in {updates['disease'].lower()}"
                )
            
            # Update titles for treatment publications
            treat_pub_mask = pub_mask & (nodes_df['node_id'].str.startswith('TREAT_PUB_'))
            if treat_pub_mask.any():
                nodes_df.loc[treat_pub_mask, 'title'] = nodes_df.loc[treat_pub_mask, 'title'].apply(
                    lambda x: f"Clinical trial results for {updates['disease']} treatment using {updates['treatment_name']}"
                )
            
            # Update titles for ecosystem publications
            eco_pub_mask = pub_mask & (nodes_df['node_id'].str.startswith('ECO_'))
            if eco_pub_mask.any():
                nodes_df.loc[eco_pub_mask, 'title'] = nodes_df.loc[eco_pub_mask, 'title'].apply(
                    lambda x: f"Translational {updates['keywords'][0]} research: From bench to bedside"
                )
            
            print(f"   ✅ Updated publication titles for Network {net_id}")
    
    # Update summary
    print(f"\\n📊 Updating Network Summary...")
    
    for net_id, updates in network_updates.items():
        summary_mask = summary_df['network_id'] == net_id
        if summary_mask.any():
            summary_df.loc[summary_mask, 'disease'] = updates['disease']
            summary_df.loc[summary_mask, 'treatment_name'] = updates['treatment_name']
            summary_df.loc[summary_mask, 'approval_year'] = updates['approval_year']
            print(f"   ✅ Updated summary for Network {net_id}")
    
    # Save updated data back to database
    print(f"\\n💾 Saving Updated Database...")
    
    nodes_df.to_sql('nodes', conn, if_exists='replace', index=False)
    edges_df.to_sql('edges', conn, if_exists='replace', index=False)  # Edges remain unchanged
    summary_df.to_sql('network_summary', conn, if_exists='replace', index=False)
    
    conn.close()
    
    # Update CSV files
    nodes_df.to_csv('streamlit_nodes.csv', index=False)
    edges_df.to_csv('streamlit_edges.csv', index=False)
    summary_df.to_csv('streamlit_summary.csv', index=False)
    
    # Update JSON backup
    database_json = {
        'nodes': nodes_df.to_dict('records'),
        'edges': edges_df.to_dict('records'),
        'summary': summary_df.to_dict('records'),
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '3.1_manual_update',
            'total_networks': len(summary_df),
            'total_nodes': len(nodes_df),
            'total_edges': len(edges_df),
            'manual_updates': [
                'Network 1: Duchenne Muscular Dystrophy → Givinostat',
                'Network 2: Huntington Disease → AMT-130',
                'Network 3: Diabetes → Smart Insulin Patch (unchanged)'
            ]
        }
    }
    
    with open('streamlit_database.json', 'w') as f:
        json.dump(database_json, f, indent=2)
    
    print(f"   ✅ SQLite database updated")
    print(f"   ✅ CSV files updated")
    print(f"   ✅ JSON backup updated")
    
    # Display final summary
    print(f"\\n🎉 Manual Update Complete!")
    print(f"=" * 50)
    print(f"📊 Updated Networks:")
    
    for _, row in summary_df.iterrows():
        net_id = row['network_id']
        disease = row['disease']
        treatment = row['treatment_name']
        approval_year = row['approval_year']
        
        if net_id in network_updates:
            print(f"   🔄 Network {net_id}: {disease} → {treatment} (approved {approval_year}) [UPDATED]")
        else:
            print(f"   ✅ Network {net_id}: {disease} → {treatment} (approved {approval_year}) [UNCHANGED]")
    
    print(f"\\n🔗 Citation patterns and network structure preserved")
    print(f"📈 Total edges maintained: {len(edges_df)}")
    print(f"🎯 Ready for Streamlit deployment!")

if __name__ == "__main__":
    update_database_manually()
