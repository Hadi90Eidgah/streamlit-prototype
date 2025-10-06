"""
Improved Multi-Network Database Generator
Enhanced with realistic citation bias patterns and guaranteed connections
"""

import json
import random
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class ImprovedStreamlitDatabaseGenerator:
    def __init__(self, seed: Optional[int] = None):
        """Initialize the improved database generator"""
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
                "color": "#FF6B6B"
            },
            {
                "disease": "Alzheimer's Disease", 
                "treatment_name": "Aducanumab Plus",
                "grant_focus": "Neurodegenerative Disease Research",
                "keywords": ["alzheimer", "amyloid", "neurodegenerative", "dementia", "brain"],
                "approval_year": 2023,
                "color": "#4ECDC4"
            },
            {
                "disease": "Diabetes",
                "treatment_name": "Smart Insulin Patch",
                "grant_focus": "Metabolic Disease Innovation",
                "keywords": ["diabetes", "insulin", "glucose", "metabolic", "endocrine"],
                "approval_year": 2025,
                "color": "#45B7D1"
            }
        ]
        
        # Research data for realistic generation
        self.authors = [
            "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Emily Rodriguez", "Dr. David Kim",
            "Dr. Jennifer Martinez", "Dr. Robert Thompson", "Dr. Lisa Anderson", "Dr. James Wilson",
            "Dr. Maria Garcia", "Dr. Christopher Lee", "Dr. Amanda Taylor", "Dr. Daniel Brown",
            "Dr. Jessica Davis", "Dr. Matthew Miller", "Dr. Rachel White", "Dr. Andrew Jackson",
            "Dr. Stephanie Thomas", "Dr. Kevin Martinez", "Dr. Nicole Johnson", "Dr. Brandon Lee"
        ]
        
        self.journals = [
            "Nature", "Science", "Cell", "Nature Medicine", "Science Translational Medicine",
            "New England Journal of Medicine", "The Lancet", "Nature Biotechnology", "PNAS",
            "Cell Metabolism", "Nature Immunology", "Journal of Clinical Investigation"
        ]
    
    def generate_pmid(self) -> int:
        """Generate realistic PMID"""
        return random.randint(10000000, 99999999)
    
    def generate_grant_id(self) -> str:
        """Generate realistic grant ID"""
        prefixes = ["INST-R01", "INST-U01", "INST-R21", "INST-P01"]
        return f"{random.choice(prefixes)}-{random.randint(100000, 999999)}"
    
    def generate_title(self, keywords: List[str], phase: str) -> str:
        """Generate realistic paper title"""
        templates = {
            "basic": [
                f"{keywords[0].title()} research: Novel therapeutic targets and mechanisms",
                f"Molecular mechanisms of {keywords[1]} in {keywords[0]} pathogenesis",
                f"Identification of {keywords[2]} pathways in {keywords[0]} development"
            ],
            "translational": [
                f"Translational {keywords[0]} research: From bench to bedside",
                f"Clinical implications of {keywords[1]} in {keywords[0]} treatment",
                f"Biomarker discovery for {keywords[0]} using {keywords[2]} approaches"
            ],
            "treatment": [
                f"Clinical trial results for {keywords[0]} treatment using {keywords[1]}",
                f"Phase II study of {keywords[2]} in {keywords[0]} patients",
                f"Efficacy and safety of novel {keywords[1]} therapy for {keywords[0]}"
            ]
        }
        return random.choice(templates.get(phase, templates["basic"]))
    
    def create_grant_node(self, network_config: Dict, network_id: int) -> Dict:
        """Create grant node"""
        grant_year = random.randint(2015, 2019)
        
        return {
            "node_id": f"GRANT_{network_id}",
            "node_type": "grant",
            "network_id": network_id,
            "grant_id": self.generate_grant_id(),
            "funding_amount": random.randint(1500000, 3000000),
            "year": grant_year,
            "pi_name": random.choice(self.authors),
            "title": f"{network_config['grant_focus']} Initiative",
            "disease": network_config["disease"],
            "treatment_name": network_config["treatment_name"],
            "approval_year": network_config["approval_year"],
            "fda_approved": 1
        }
    
    def create_publication_node(self, node_id: str, year: int, keywords: List[str], 
                              phase: str, network_id: int, funded_by_grant: bool = False,
                              treatment_related: bool = False) -> Dict:
        """Create publication node with enhanced metadata"""
        
        pmid = self.generate_pmid()
        num_authors = random.randint(2, 8)
        authors = random.sample(self.authors, num_authors)
        
        return {
            "node_id": node_id,
            "node_type": "publication",
            "network_id": network_id,
            "pmid": pmid,
            "year": year,
            "title": self.generate_title(keywords, phase),
            "authors": ", ".join(authors),
            "journal": random.choice(self.journals),
            "funded_by_grant": 1 if funded_by_grant else 0,
            "treatment_related": 1 if treatment_related else 0
        }
    
    def create_treatment_node(self, network_config: Dict, network_id: int) -> Dict:
        """Create treatment node"""
        return {
            "node_id": f"TREAT_{network_id}",
            "node_type": "treatment",
            "network_id": network_id,
            "treatment_name": network_config["treatment_name"],
            "approval_year": network_config["approval_year"],
            "disease": network_config["disease"],
            "fda_approved": 1
        }
    
    def calculate_citation_probability(self, citing_paper: Dict, cited_paper: Dict, 
                                     grant_papers: List[Dict], treatment_papers: List[Dict]) -> float:
        """
        Calculate citation probability based on proximity and paper types
        Higher probability for papers closer in time and research pathway
        """
        
        # Base probability
        base_prob = 0.1
        
        # Time proximity bonus (newer cites older)
        if citing_paper["year"] <= cited_paper["year"]:
            return 0.0  # Can't cite future papers
        
        time_diff = citing_paper["year"] - cited_paper["year"]
        if time_diff <= 2:
            time_bonus = 0.4
        elif time_diff <= 4:
            time_bonus = 0.2
        else:
            time_bonus = 0.05
        
        # Paper type proximity bonuses
        citing_is_treatment = citing_paper["node_id"] in [p["node_id"] for p in treatment_papers]
        cited_is_grant = cited_paper["node_id"] in [p["node_id"] for p in grant_papers]
        cited_is_treatment = cited_paper["node_id"] in [p["node_id"] for p in treatment_papers]
        
        # Treatment papers cite more within their layer
        if citing_is_treatment and cited_is_treatment:
            proximity_bonus = 0.6  # High within treatment layer
        elif citing_is_treatment and not cited_is_grant:
            proximity_bonus = 0.3  # Medium for ecosystem papers
        elif citing_is_treatment and cited_is_grant:
            proximity_bonus = 0.1  # Lower for grant papers (but still possible)
        else:
            proximity_bonus = 0.2  # Standard for other combinations
        
        return min(base_prob + time_bonus + proximity_bonus, 0.9)
    
    def generate_biased_citations(self, nodes: List[Dict], network_id: int) -> List[Dict]:
        """
        Generate citations with realistic bias patterns
        """
        edges = []
        
        # Separate node types
        grant_papers = [n for n in nodes if n["node_id"].startswith("PUB_")]
        treatment_papers = [n for n in nodes if n["node_id"].startswith("TREAT_PUB_")]
        ecosystem_papers = [n for n in nodes if n["node_id"].startswith("ECO_")]
        all_publications = grant_papers + treatment_papers + ecosystem_papers
        
        print(f"  📊 Citation Generation for Network {network_id}:")
        print(f"     Grant papers: {len(grant_papers)}")
        print(f"     Treatment papers: {len(treatment_papers)}")
        print(f"     Ecosystem papers: {len(ecosystem_papers)}")
        
        # 1. GUARANTEED: Treatment papers must cite at least 1-3 grant papers
        for treatment_paper in treatment_papers:
            # Guarantee at least 1, at most 3 citations to grant papers
            num_grant_citations = random.randint(1, min(3, len(grant_papers)))
            selected_grant_papers = random.sample(grant_papers, num_grant_citations)
            
            for grant_paper in selected_grant_papers:
                if treatment_paper["year"] > grant_paper["year"]:
                    edges.append({
                        "source_id": treatment_paper["node_id"],
                        "target_id": grant_paper["node_id"],
                        "edge_type": "leads_to_treatment",
                        "network_id": network_id
                    })
        
        # 2. Generate all other citations with bias
        for citing_paper in all_publications:
            for cited_paper in all_publications:
                if citing_paper["node_id"] != cited_paper["node_id"]:
                    prob = self.calculate_citation_probability(
                        citing_paper, cited_paper, grant_papers, treatment_papers
                    )
                    
                    if random.random() < prob:
                        # Avoid duplicate leads_to_treatment edges
                        edge_type = "cites"
                        if (citing_paper["node_id"].startswith("TREAT_PUB_") and 
                            cited_paper["node_id"].startswith("PUB_")):
                            # Check if this edge already exists as leads_to_treatment
                            existing_edge = any(
                                e["source_id"] == citing_paper["node_id"] and 
                                e["target_id"] == cited_paper["node_id"] and 
                                e["edge_type"] == "leads_to_treatment"
                                for e in edges
                            )
                            if not existing_edge:
                                edge_type = "leads_to_treatment"
                        
                        edges.append({
                            "source_id": citing_paper["node_id"],
                            "target_id": cited_paper["node_id"],
                            "edge_type": edge_type,
                            "network_id": network_id
                        })
        
        # Count edge types for reporting
        citation_counts = {}
        for edge in edges:
            edge_type = edge["edge_type"]
            citation_counts[edge_type] = citation_counts.get(edge_type, 0) + 1
        
        print(f"     Generated citations: {citation_counts}")
        
        return edges
    
    def generate_single_network(self, network_config: Dict, network_id: int) -> Tuple[List[Dict], List[Dict]]:
        """Generate one complete citation network with improved bias"""
        
        print(f"🔬 Generating Network {network_id}: {network_config['disease']}")
        
        nodes = []
        edges = []
        
        # 1. Create grant
        grant = self.create_grant_node(network_config, network_id)
        nodes.append(grant)
        grant_year = grant["year"]
        
        # 2. Create grant-funded publications (4 papers)
        grant_papers = []
        for i in range(1, 5):
            node_id = f"PUB_{network_id}_{i}"
            year = random.randint(grant_year + 1, grant_year + 3)
            paper = self.create_publication_node(
                node_id, year, network_config["keywords"], "basic", 
                network_id, funded_by_grant=True
            )
            nodes.append(paper)
            grant_papers.append(paper)
            
            # GUARANTEED: Grant funds paper
            edges.append({
                "source_id": grant["node_id"],
                "target_id": paper["node_id"],
                "edge_type": "funded_by",
                "network_id": network_id
            })
        
        # 3. Create ecosystem publications (25 papers)
        ecosystem_papers = []
        for i in range(1, 26):
            node_id = f"ECO_{network_id}_{i}"
            year = random.randint(grant_year + 2, network_config["approval_year"] - 2)
            phase = random.choices(["basic", "translational"], weights=[0.7, 0.3])[0]
            paper = self.create_publication_node(
                node_id, year, network_config["keywords"], phase, network_id
            )
            nodes.append(paper)
            ecosystem_papers.append(paper)
        
        # 4. Create treatment pathway publications (3 papers)
        treatment_papers = []
        for i in range(1, 4):
            node_id = f"TREAT_PUB_{network_id}_{i}"
            year = random.randint(network_config["approval_year"] - 3, network_config["approval_year"] - 1)
            paper = self.create_publication_node(
                node_id, year, network_config["keywords"], "treatment", 
                network_id, treatment_related=True
            )
            nodes.append(paper)
            treatment_papers.append(paper)
        
        # 5. Create final treatment
        treatment = self.create_treatment_node(network_config, network_id)
        nodes.append(treatment)
        
        # GUARANTEED: Treatment papers enable final treatment
        for treatment_paper in treatment_papers:
            edges.append({
                "source_id": treatment_paper["node_id"],
                "target_id": treatment["node_id"],
                "edge_type": "enables_treatment",
                "network_id": network_id
            })
        
        # 6. Generate biased citations
        citation_edges = self.generate_biased_citations(nodes, network_id)
        edges.extend(citation_edges)
        
        print(f"   ✅ {len(nodes)} nodes, {len(edges)} edges generated")
        
        return nodes, edges
    
    def generate_complete_database(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate all 3 networks with improved citation patterns"""
        
        all_nodes = []
        all_edges = []
        
        print("🏥 Generating IMPROVED Research Impact Database")
        print("=" * 60)
        print("Enhanced with realistic citation bias and guaranteed connections\\n")
        
        for i, network_config in enumerate(self.networks, 1):
            nodes, edges = self.generate_single_network(network_config, i)
            all_nodes.extend(nodes)
            all_edges.extend(edges)
            print()
        
        nodes_df = pd.DataFrame(all_nodes)
        edges_df = pd.DataFrame(all_edges)
        
        # Generate summary statistics
        summary_data = []
        for i, network_config in enumerate(self.networks, 1):
            network_nodes = nodes_df[nodes_df['network_id'] == i]
            network_edges = edges_df[edges_df['network_id'] == i]
            
            grant_node = network_nodes[network_nodes['node_type'] == 'grant'].iloc[0]
            
            summary_data.append({
                'network_id': i,
                'disease': network_config['disease'],
                'treatment_name': network_config['treatment_name'],
                'grant_id': grant_node['grant_id'],
                'grant_year': int(grant_node['year']),
                'approval_year': network_config['approval_year'],
                'funding_amount': int(grant_node['funding_amount']),
                'total_publications': len(network_nodes[network_nodes['node_type'] == 'publication']),
                'research_duration': network_config['approval_year'] - int(grant_node['year'])
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        print(f"📊 IMPROVED Database Summary:")
        print(f"   🎯 Total Networks: {len(self.networks)}")
        print(f"   📄 Total Nodes: {len(nodes_df)}")
        print(f"   🔗 Total Edges: {len(edges_df)}")
        print(f"   💰 Total Funding: ${nodes_df[nodes_df['node_type']=='grant']['funding_amount'].sum():,.0f}")
        
        # Edge type breakdown
        edge_counts = edges_df['edge_type'].value_counts()
        print(f"\\n🔗 Edge Type Breakdown:")
        for edge_type, count in edge_counts.items():
            print(f"   {edge_type}: {count}")
        
        return nodes_df, edges_df, summary_df
    
    def save_for_streamlit(self, nodes_df: pd.DataFrame, edges_df: pd.DataFrame, summary_df: pd.DataFrame):
        """Save improved database in multiple formats"""
        
        print("\\n💾 Saving Improved Database...")
        
        # 1. SQLite database (primary format)
        conn = sqlite3.connect("streamlit_research_database.db")
        nodes_df.to_sql('nodes', conn, if_exists='replace', index=False)
        edges_df.to_sql('edges', conn, if_exists='replace', index=False)
        summary_df.to_sql('network_summary', conn, if_exists='replace', index=False)
        conn.close()
        
        # 2. CSV files (backup format)
        nodes_df.to_csv('streamlit_nodes.csv', index=False)
        edges_df.to_csv('streamlit_edges.csv', index=False)
        summary_df.to_csv('streamlit_summary.csv', index=False)
        
        # 3. JSON backup
        database_json = {
            'nodes': nodes_df.to_dict('records'),
            'edges': edges_df.to_dict('records'),
            'summary': summary_df.to_dict('records'),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '2.0_improved',
                'total_networks': len(self.networks),
                'total_nodes': len(nodes_df),
                'total_edges': len(edges_df)
            }
        }
        
        with open('streamlit_database.json', 'w') as f:
            json.dump(database_json, f, indent=2)
        
        print("   ✅ SQLite database: streamlit_research_database.db")
        print("   ✅ CSV files: streamlit_nodes.csv, streamlit_edges.csv, streamlit_summary.csv")
        print("   ✅ JSON backup: streamlit_database.json")

def main():
    """Generate improved database with realistic citation patterns"""
    
    print("🚀 Starting Improved Database Generation...")
    print("Features: Guaranteed connections + Realistic citation bias\\n")
    
    # Initialize generator with seed for reproducibility
    generator = ImprovedStreamlitDatabaseGenerator(seed=42)
    
    # Generate complete database
    nodes_df, edges_df, summary_df = generator.generate_complete_database()
    
    # Save in multiple formats
    generator.save_for_streamlit(nodes_df, edges_df, summary_df)
    
    print("\\n🎉 Improved Database Generation Complete!")
    print("Ready for Streamlit prototype with enhanced citation patterns.")

if __name__ == "__main__":
    main()
