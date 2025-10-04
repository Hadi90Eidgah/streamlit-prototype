"""
Multi-Network Database Generator - Google Colab Version
Generates 3 citation networks for Streamlit prototype
Perfect for demonstrating research impact to stakeholders
"""

# Install required packages (uncomment if needed in Colab)
# !pip install pandas sqlite3

import json
import random
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class StreamlitDatabaseGenerator:
    def __init__(self, seed: Optional[int] = None):
        """Initialize the database generator for Streamlit prototype"""
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        # 3 Disease/Treatment networks for stakeholder demo
        self.networks = [
            {
                "disease": "Cancer",
                "treatment_name": "CAR-T Cell Therapy",
                "grant_focus": "Immunotherapy Research",
                "keywords": ["immunotherapy", "T-cell", "cancer", "oncology", "CAR-T"],
                "approval_year": 2024,
                "color": "#FF6B6B"  # Red for cancer
            },
            {
                "disease": "Alzheimer's Disease", 
                "treatment_name": "Aducanumab Plus",
                "grant_focus": "Neurodegenerative Disease Research",
                "keywords": ["alzheimer", "amyloid", "neurodegenerative", "dementia", "brain"],
                "approval_year": 2023,
                "color": "#4ECDC4"  # Teal for neurological
            },
            {
                "disease": "Diabetes",
                "treatment_name": "Smart Insulin Patch",
                "grant_focus": "Metabolic Disease Innovation",
                "keywords": ["diabetes", "insulin", "glucose", "metabolic", "endocrine"],
                "approval_year": 2025,
                "color": "#45B7D1"  # Blue for metabolic
            }
        ]
        
        # Realistic author names
        self.authors = [
            "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Jennifer Rodriguez", "Dr. David Kim",
            "Dr. Lisa Wang", "Dr. Robert Martinez", "Dr. Maria Garcia", "Dr. James Wilson",
            "Dr. Emily Brown", "Dr. Christopher Lee", "Dr. Jessica Davis", "Dr. Daniel Miller",
            "Dr. Amanda Taylor", "Dr. Matthew Anderson", "Dr. Stephanie White", "Dr. Joshua Harris"
        ]
        
        # Top-tier journals
        self.journals = [
            "Nature", "Science", "Cell", "The Lancet", "NEJM",
            "Nature Medicine", "Nature Biotechnology", "Science Translational Medicine",
            "Journal of Clinical Investigation", "PNAS", "Nature Immunology"
        ]
    
    def generate_pmid(self) -> int:
        """Generate realistic PMID"""
        return random.randint(10000000, 99999999)
    
    def generate_grant_id(self) -> str:
        """Generate institutional grant ID"""
        types = ["R01", "R21", "P01", "U01"]
        return f"INST-{random.choice(types)}-{random.randint(100000, 999999)}"
    
    def generate_title(self, keywords: List[str], research_phase: str) -> str:
        """Generate realistic publication title"""
        templates = {
            "basic": [
                f"Novel {random.choice(keywords)} mechanisms in disease pathogenesis",
                f"Molecular characterization of {random.choice(keywords)} pathways",
                f"Role of {random.choice(keywords)} in disease progression",
                f"Identification of {random.choice(keywords)} biomarkers"
            ],
            "translational": [
                f"Clinical translation of {random.choice(keywords)}-based therapies",
                f"Phase I trial of {random.choice(keywords)} inhibitors",
                f"Safety and efficacy of {random.choice(keywords)} treatment",
                f"Biomarker-driven {random.choice(keywords)} therapy"
            ],
            "treatment": [
                f"Breakthrough {random.choice(keywords)} therapy shows promise",
                f"Long-term outcomes of {random.choice(keywords)}-based treatment",
                f"Real-world evidence for {random.choice(keywords)} treatment",
                f"Cost-effectiveness of {random.choice(keywords)} therapy"
            ]
        }
        return random.choice(templates[research_phase])
    
    def create_grant_node(self, network_config: Dict, network_id: int) -> Dict:
        """Create grant node"""
        grant_year = random.randint(2015, 2019)  # Grants start early
        
        return {
            "node_id": f"GRANT_{network_id}",
            "node_type": "grant",
            "network_id": network_id,
            "grant_id": self.generate_grant_id(),
            "year": grant_year,
            "funding_amount": random.randint(500000, 5000000),
            "disease_focus": network_config["disease"],
            "research_focus": network_config["grant_focus"],
            "institution": "Your Research Institution",
            "pi_name": random.choice(self.authors),
            "node_label": f"Grant: {network_config['grant_focus']}"
        }
    
    def create_publication_node(self, pmid: int, year: int, keywords: List[str], 
                              phase: str, network_id: int) -> Dict:
        """Create publication node with realistic data"""
        
        # Generate 1-6 authors
        num_authors = random.randint(1, 6)
        authors = random.sample(self.authors, num_authors)
        
        return {
            "node_id": str(pmid),
            "node_type": "publication",
            "network_id": network_id,
            "pmid": pmid,
            "title": self.generate_title(keywords, phase),
            "authors": ", ".join(authors),
            "journal": random.choice(self.journals),
            "year": year,
            "citations": random.randint(5, 500),
            "impact_factor": round(random.uniform(5.0, 45.0), 2),
            "research_phase": phase,
            "node_label": f"PMID {pmid}: {self.generate_title(keywords, phase)[:40]}..."
        }
    
    def create_treatment_node(self, network_config: Dict, network_id: int) -> Dict:
        """Create treatment node"""
        return {
            "node_id": f"TREAT_{network_id}",
            "node_type": "treatment",
            "network_id": network_id,
            "treatment_name": network_config["treatment_name"],
            "disease": network_config["disease"],
            "approval_year": network_config["approval_year"],
            "phase": "FDA Approved",
            "indication": f"{network_config['disease']} Treatment",
            "node_label": f"Treatment: {network_config['treatment_name']}"
        }
    
    def generate_single_network(self, network_config: Dict, network_id: int) -> Tuple[List[Dict], List[Dict]]:
        """Generate one complete citation network"""
        
        nodes = []
        edges = []
        
        # 1. Create grant
        grant = self.create_grant_node(network_config, network_id)
        nodes.append(grant)
        grant_year = grant["year"]
        
        # 2. Create initial research (4 papers funded by grant)
        initial_papers = []
        for i in range(4):
            pmid = self.generate_pmid()
            year = random.randint(grant_year + 1, grant_year + 3)
            paper = self.create_publication_node(pmid, year, network_config["keywords"], "basic", network_id)
            nodes.append(paper)
            initial_papers.append(paper)
            
            # Grant funds paper
            edges.append({
                "source_id": grant["node_id"],
                "target_id": paper["node_id"],
                "edge_type": "funded_by",
                "weight": 1.0,
                "network_id": network_id
            })
        
        # 3. Create research ecosystem (30 papers)
        research_papers = []
        for i in range(30):
            pmid = self.generate_pmid()
            year = random.randint(grant_year + 2, network_config["approval_year"] - 2)
            phase = random.choices(["basic", "translational"], weights=[0.7, 0.3])[0]
            paper = self.create_publication_node(pmid, year, network_config["keywords"], phase, network_id)
            nodes.append(paper)
            research_papers.append(paper)
        
        # 4. Create treatment pathway (3 papers)
        treatment_papers = []
        for i in range(3):
            pmid = self.generate_pmid()
            year = random.randint(network_config["approval_year"] - 3, network_config["approval_year"] - 1)
            paper = self.create_publication_node(pmid, year, network_config["keywords"], "treatment", network_id)
            nodes.append(paper)
            treatment_papers.append(paper)
        
        # 5. Create final treatment
        treatment = self.create_treatment_node(network_config, network_id)
        nodes.append(treatment)
        
        # 6. Generate citations
        all_papers = initial_papers + research_papers + treatment_papers
        
        # Initial papers cite research papers
        for initial in initial_papers:
            citations = random.sample(research_papers, random.randint(3, 8))
            for cited in citations:
                if cited["year"] >= initial["year"]:
                    edges.append({
                        "source_id": initial["node_id"],
                        "target_id": cited["node_id"],
                        "edge_type": "cites",
                        "weight": random.uniform(0.3, 1.0),
                        "network_id": network_id
                    })
        
        # Research papers cite each other (15% probability)
        for i, paper1 in enumerate(research_papers):
            for paper2 in research_papers[i+1:]:
                if random.random() < 0.15:
                    edges.append({
                        "source_id": paper1["node_id"],
                        "target_id": paper2["node_id"],
                        "edge_type": "cites",
                        "weight": random.uniform(0.1, 0.8),
                        "network_id": network_id
                    })
        
        # Research leads to treatment papers
        precursors = random.sample(research_papers, 8)
        for precursor in precursors:
            for treatment_paper in random.sample(treatment_papers, random.randint(1, 2)):
                if treatment_paper["year"] >= precursor["year"]:
                    edges.append({
                        "source_id": precursor["node_id"],
                        "target_id": treatment_paper["node_id"],
                        "edge_type": "leads_to_treatment",
                        "weight": random.uniform(0.6, 1.0),
                        "network_id": network_id
                    })
        
        # Treatment papers enable final treatment
        for treatment_paper in treatment_papers:
            edges.append({
                "source_id": treatment_paper["node_id"],
                "target_id": treatment["node_id"],
                "edge_type": "enables_treatment",
                "weight": 1.0,
                "network_id": network_id
            })
        
        return nodes, edges
    
    def generate_complete_database(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate all 3 networks for Streamlit prototype"""
        
        all_nodes = []
        all_edges = []
        
        print("🏥 Generating Research Impact Database for Stakeholder Demo")
        print("=" * 65)
        print("Showing how institutional funding leads to breakthrough treatments\\n")
        
        for i, network_config in enumerate(self.networks, 1):
            print(f"🔬 Network {i}: {network_config['disease']} Research")
            print(f"   Grant → Research → {network_config['treatment_name']}")
            
            nodes, edges = self.generate_single_network(network_config, i)
            all_nodes.extend(nodes)
            all_edges.extend(edges)
            
            print(f"   ✅ {len(nodes)} nodes, {len(edges)} connections\\n")
        
        nodes_df = pd.DataFrame(all_nodes)
        edges_df = pd.DataFrame(all_edges)
        
        print(f"📊 Complete Database Summary:")
        print(f"   🎯 Total Networks: {len(self.networks)}")
        print(f"   📄 Total Nodes: {len(nodes_df)}")
        print(f"   🔗 Total Connections: {len(edges_df)}")
        print(f"   💰 Total Funding: ${nodes_df[nodes_df['node_type']=='grant']['funding_amount'].sum():,.0f}")
        
        return nodes_df, edges_df
    
    def save_for_streamlit(self, nodes_df: pd.DataFrame, edges_df: pd.DataFrame):
        """Save in formats perfect for Streamlit development"""
        
        # 1. Save to SQLite (best for Streamlit)
        conn = sqlite3.connect("streamlit_research_database.db")
        nodes_df.to_sql('nodes', conn, if_exists='replace', index=False)
        edges_df.to_sql('edges', conn, if_exists='replace', index=False)
        
        # Create network summary for Streamlit dashboard
        summary_data = []
        for i, config in enumerate(self.networks, 1):
            network_nodes = nodes_df[nodes_df['network_id'] == i]
            network_edges = edges_df[edges_df['network_id'] == i]
            grant = network_nodes[network_nodes['node_type'] == 'grant'].iloc[0]
            treatment = network_nodes[network_nodes['node_type'] == 'treatment'].iloc[0]
            
            summary_data.append({
                'network_id': i,
                'disease': config['disease'],
                'treatment_name': config['treatment_name'],
                'grant_id': grant['grant_id'],
                'grant_year': grant['year'],
                'approval_year': treatment['approval_year'],
                'funding_amount': grant['funding_amount'],
                'total_publications': len(network_nodes[network_nodes['node_type'] == 'publication']),
                'research_duration': treatment['approval_year'] - grant['year'],
                'color': config['color']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_sql('network_summary', conn, if_exists='replace', index=False)
        conn.close()
        
        # 2. Save to CSV (for GitHub repository)
        nodes_df.to_csv("streamlit_nodes.csv", index=False)
        edges_df.to_csv("streamlit_edges.csv", index=False)
        summary_df.to_csv("streamlit_summary.csv", index=False)
        
        # 3. Save to JSON (for web APIs)
        database = {
            "metadata": {
                "generated_for": "Streamlit Prototype",
                "purpose": "Demonstrate Research Impact to Stakeholders",
                "total_networks": len(self.networks),
                "total_funding": int(nodes_df[nodes_df['node_type']=='grant']['funding_amount'].sum()),
                "diseases": [n["disease"] for n in self.networks],
                "treatments": [n["treatment_name"] for n in self.networks]
            },
            "networks": summary_data,
            "nodes": nodes_df.to_dict('records'),
            "edges": edges_df.to_dict('records')
        }
        
        with open("streamlit_database.json", 'w') as f:
            json.dump(database, f, indent=2, default=str)
        
        print(f"\\n💾 Streamlit-Ready Files Generated:")
        print(f"   🗄️  streamlit_research_database.db (SQLite)")
        print(f"   📊 streamlit_nodes.csv")
        print(f"   🔗 streamlit_edges.csv") 
        print(f"   📈 streamlit_summary.csv")
        print(f"   📄 streamlit_database.json")
        
        return summary_df

def generate_streamlit_database(seed=42):
    """Main function for Google Colab - generates Streamlit-ready database"""
    
    print("🚀 Streamlit Research Database Generator")
    print("Perfect for demonstrating fundraising ROI to stakeholders!\\n")
    
    # Generate database
    generator = StreamlitDatabaseGenerator(seed=seed)
    nodes_df, edges_df = generator.generate_complete_database()
    summary_df = generator.save_for_streamlit(nodes_df, edges_df)
    
    print(f"\\n🎯 Ready for Streamlit Development!")
    print(f"📁 Upload files to GitHub repository")
    print(f"🔗 Connect Streamlit app to database")
    print(f"📊 Build interactive dashboard for stakeholders")
    
    # Display sample data
    print(f"\\n📋 Network Summary for Stakeholders:")
    for _, row in summary_df.iterrows():
        print(f"   {row['disease']}: ${row['funding_amount']:,.0f} → {row['treatment_name']} ({row['research_duration']} years)")
    
    return nodes_df, edges_df, summary_df

# Google Colab execution
if __name__ == "__main__":
    # Generate the complete Streamlit database
    nodes_df, edges_df, summary_df = generate_streamlit_database(seed=42)
    
    # Show sample data for verification
    print("\\n📊 Sample Grant Data:")
    print(nodes_df[nodes_df['node_type'] == 'grant'][['grant_id', 'disease_focus', 'funding_amount', 'year']])
    
    print("\\n📊 Sample Publication Data:")
    print(nodes_df[nodes_df['node_type'] == 'publication'][['pmid', 'title', 'authors', 'journal', 'year']].head())
    
    print("\\n📊 Sample Treatment Data:")
    print(nodes_df[nodes_df['node_type'] == 'treatment'][['treatment_name', 'disease', 'approval_year']])
    
    print("\\n✅ Database ready for Streamlit prototype development!")
