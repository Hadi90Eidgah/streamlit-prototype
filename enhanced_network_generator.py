"""
Enhanced Multi-Network Database Generator
Realistic citation chains with temporal layers and selective bridging
"""

import json
import random
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class EnhancedStreamlitDatabaseGenerator:
    def __init__(self, seed: Optional[int] = None):
        """Initialize the enhanced database generator"""
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        # 3 Disease/Treatment networks with different chain requirements
        self.networks = [
            {
                "disease": "Cancer",
                "treatment_name": "CAR-T Cell Therapy",
                "grant_focus": "Immunotherapy Research",
                "keywords": ["immunotherapy", "T-cell", "cancer", "oncology", "CAR-T"],
                "approval_year": 2024,
                "color": "#FF6B6B",
                "guaranteed_chains": 1  # Minimum 1 chain
            },
            {
                "disease": "Alzheimer's Disease", 
                "treatment_name": "Aducanumab Plus",
                "grant_focus": "Neurodegenerative Disease Research",
                "keywords": ["alzheimer", "amyloid", "neurodegenerative", "dementia", "brain"],
                "approval_year": 2023,
                "color": "#4ECDC4",
                "guaranteed_chains": 2  # 2 chains
            },
            {
                "disease": "Diabetes",
                "treatment_name": "Smart Insulin Patch",
                "grant_focus": "Metabolic Disease Innovation",
                "keywords": ["diabetes", "insulin", "glucose", "metabolic", "endocrine"],
                "approval_year": 2025,
                "color": "#45B7D1",
                "guaranteed_chains": 3  # 3 chains
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
            "treatment_related": 1 if treatment_related else 0,
            "citation_count": 0  # Will be calculated later
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
    
    def create_temporal_layers(self, papers: List[Dict]) -> Dict[int, List[Dict]]:
        """Organize papers into temporal layers by year"""
        layers = {}
        for paper in papers:
            year = paper["year"]
            if year not in layers:
                layers[year] = []
            layers[year].append(paper)
        return layers
    
    def select_bridge_papers(self, ecosystem_papers: List[Dict], num_bridges: int) -> List[Dict]:
        """Select the most cited ecosystem papers to serve as bridges"""
        # Sort by year (older papers tend to be more cited)
        sorted_papers = sorted(ecosystem_papers, key=lambda x: x["year"])
        
        # Select papers from earlier years as potential bridges
        early_papers = sorted_papers[:len(sorted_papers)//2]
        
        # Select bridge papers
        num_bridges = min(num_bridges, len(early_papers))
        bridge_papers = random.sample(early_papers, num_bridges)
        
        # Mark them as highly cited
        for paper in bridge_papers:
            paper["citation_count"] = random.randint(50, 150)
        
        return bridge_papers
    
    def generate_realistic_citations(self, nodes: List[Dict], network_config: Dict, network_id: int) -> List[Dict]:
        """
        Generate realistic citation patterns with temporal layers and selective bridging
        """
        edges = []
        
        # Separate node types
        grant_papers = [n for n in nodes if n["node_id"].startswith("PUB_")]
        treatment_papers = [n for n in nodes if n["node_id"].startswith("TREAT_PUB_")]
        ecosystem_papers = [n for n in nodes if n["node_id"].startswith("ECO_")]
        all_publications = grant_papers + treatment_papers + ecosystem_papers
        
        print(f"  📊 Enhanced Citation Generation for Network {network_id}:")
        print(f"     Grant papers: {len(grant_papers)}")
        print(f"     Treatment papers: {len(treatment_papers)}")
        print(f"     Ecosystem papers: {len(ecosystem_papers)}")
        
        # Create temporal layers
        ecosystem_layers = self.create_temporal_layers(ecosystem_papers)
        
        # Select bridge papers (most cited ecosystem papers)
        num_guaranteed_chains = network_config["guaranteed_chains"]
        bridge_papers = self.select_bridge_papers(ecosystem_papers, num_guaranteed_chains * 2)
        
        print(f"     Bridge papers selected: {len(bridge_papers)}")
        print(f"     Guaranteed chains required: {num_guaranteed_chains}")
        
        # 1. GUARANTEED CHAINS: Treatment → Bridge Ecosystem → Selected Grant Papers
        selected_grant_papers = random.sample(grant_papers, min(num_guaranteed_chains, len(grant_papers)))
        
        for i, treatment_paper in enumerate(treatment_papers):
            if i < num_guaranteed_chains:
                # Select a bridge paper for this chain
                bridge_paper = random.choice(bridge_papers)
                target_grant = selected_grant_papers[i % len(selected_grant_papers)]
                
                # Treatment → Bridge Ecosystem
                edges.append({
                    "source_id": treatment_paper["node_id"],
                    "target_id": bridge_paper["node_id"],
                    "edge_type": "leads_to_treatment",
                    "network_id": network_id
                })
                
                # Bridge Ecosystem → Grant (via regular citation)
                edges.append({
                    "source_id": bridge_paper["node_id"],
                    "target_id": target_grant["node_id"],
                    "edge_type": "cites",
                    "network_id": network_id
                })
                
                print(f"     Chain {i+1}: {treatment_paper['node_id']} → {bridge_paper['node_id']} → {target_grant['node_id']}")
        
        # 2. TEMPORAL LAYER CITATIONS: Newer ecosystem papers cite older ones
        sorted_years = sorted(ecosystem_layers.keys())
        for i, year in enumerate(sorted_years[1:], 1):  # Start from second year
            current_papers = ecosystem_layers[year]
            
            # Cite papers from previous years
            for prev_year in sorted_years[:i]:
                prev_papers = ecosystem_layers[prev_year]
                
                for current_paper in current_papers:
                    # Higher probability to cite recent papers, lower for older
                    year_diff = year - prev_year
                    if year_diff <= 2:
                        cite_prob = 0.4
                    elif year_diff <= 4:
                        cite_prob = 0.2
                    else:
                        cite_prob = 0.1
                    
                    # Select papers to cite
                    num_citations = random.randint(0, 3)
                    if num_citations > 0 and random.random() < cite_prob:
                        cited_papers = random.sample(prev_papers, min(num_citations, len(prev_papers)))
                        for cited_paper in cited_papers:
                            edges.append({
                                "source_id": current_paper["node_id"],
                                "target_id": cited_paper["node_id"],
                                "edge_type": "cites",
                                "network_id": network_id
                            })
        
        # 3. TREATMENT PAPERS → ECOSYSTEM PAPERS (High probability, avoid direct grant citations)
        for treatment_paper in treatment_papers:
            # High probability to cite ecosystem papers
            num_eco_citations = random.randint(3, 8)
            potential_targets = [p for p in ecosystem_papers if p["year"] < treatment_paper["year"]]
            
            if potential_targets:
                # Prefer bridge papers and recent ecosystem papers
                weighted_targets = bridge_papers + potential_targets[-10:]  # Recent papers
                # Remove duplicates by node_id
                seen_ids = set()
                unique_targets = []
                for target in weighted_targets:
                    if target["node_id"] not in seen_ids:
                        unique_targets.append(target)
                        seen_ids.add(target["node_id"])
                
                selected_targets = random.sample(
                    unique_targets, 
                    min(num_eco_citations, len(unique_targets))
                )
                
                for target in selected_targets:
                    # Avoid duplicate edges
                    existing_edge = any(
                        e["source_id"] == treatment_paper["node_id"] and 
                        e["target_id"] == target["node_id"]
                        for e in edges
                    )
                    if not existing_edge:
                        edges.append({
                            "source_id": treatment_paper["node_id"],
                            "target_id": target["node_id"],
                            "edge_type": "leads_to_treatment",
                            "network_id": network_id
                        })
        
        # 4. NO DIRECT CITATIONS: Treatment papers never cite grant papers directly
        # This creates more realistic citation patterns where treatment papers
        # only cite through the research ecosystem (ecosystem papers cite grants)
        
        # 4. ECOSYSTEM → GRANT CITATIONS (Medium probability for non-bridge papers)
        for eco_paper in ecosystem_papers:
            if eco_paper not in bridge_papers:  # Non-bridge papers
                for grant_paper in grant_papers:
                    if (eco_paper["year"] > grant_paper["year"] and 
                        random.random() < 0.15):  # 15% probability
                        
                        edges.append({
                            "source_id": eco_paper["node_id"],
                            "target_id": grant_paper["node_id"],
                            "edge_type": "cites",
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
        """Generate one complete citation network with enhanced realistic patterns"""
        
        print(f"🔬 Generating Enhanced Network {network_id}: {network_config['disease']}")
        
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
        
        # 3. Create ecosystem publications (25 papers) with temporal distribution
        ecosystem_papers = []
        for i in range(1, 26):
            node_id = f"ECO_{network_id}_{i}"
            # Distribute across years with more recent papers
            year_range = network_config["approval_year"] - grant_year - 2
            year_weights = [1, 2, 3, 4, 4, 3, 2, 1][:year_range]  # Peak in middle years
            year_offset = random.choices(range(2, year_range + 2), weights=year_weights[:year_range])[0]
            year = grant_year + year_offset
            
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
        
        # 6. Generate enhanced realistic citations
        citation_edges = self.generate_realistic_citations(nodes, network_config, network_id)
        edges.extend(citation_edges)
        
        print(f"   ✅ {len(nodes)} nodes, {len(edges)} edges generated")
        
        return nodes, edges
    
    def generate_complete_database(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate all 3 networks with enhanced realistic citation patterns"""
        
        all_nodes = []
        all_edges = []
        
        print("🏥 Generating ENHANCED Research Impact Database")
        print("=" * 65)
        print("Realistic citation chains with temporal layers and selective bridging\\n")
        
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
                'research_duration': network_config['approval_year'] - int(grant_node['year']),
                'guaranteed_chains': network_config['guaranteed_chains']
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        print(f"📊 ENHANCED Database Summary:")
        print(f"   🎯 Total Networks: {len(self.networks)}")
        print(f"   📄 Total Nodes: {len(nodes_df)}")
        print(f"   🔗 Total Edges: {len(edges_df)}")
        print(f"   💰 Total Funding: ${nodes_df[nodes_df['node_type']=='grant']['funding_amount'].sum():,.0f}")
        
        # Edge type breakdown
        edge_counts = edges_df['edge_type'].value_counts()
        print(f"\\n🔗 Edge Type Breakdown:")
        for edge_type, count in edge_counts.items():
            print(f"   {edge_type}: {count}")
        
        # Chain analysis
        print(f"\\n🔗 Guaranteed Chain Distribution:")
        for i, network_config in enumerate(self.networks, 1):
            network_edges = edges_df[edges_df['network_id'] == i]
            treatment_edges = len(network_edges[network_edges['edge_type'] == 'leads_to_treatment'])
            print(f"   Network {i} ({network_config['disease']}): {treatment_edges} treatment connections")
        
        return nodes_df, edges_df, summary_df
    
    def save_for_streamlit(self, nodes_df: pd.DataFrame, edges_df: pd.DataFrame, summary_df: pd.DataFrame):
        """Save enhanced database in multiple formats"""
        
        print("\\n💾 Saving Enhanced Database...")
        
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
                'version': '3.0_enhanced_realistic',
                'total_networks': len(self.networks),
                'total_nodes': len(nodes_df),
                'total_edges': len(edges_df),
                'features': [
                    'Temporal citation layers',
                    'Selective bridge papers',
                    'Guaranteed citation chains',
                    'Realistic direct citation probability (5%)',
                    'Variable chain requirements per network'
                ]
            }
        }
        
        with open('streamlit_database.json', 'w') as f:
            json.dump(database_json, f, indent=2)
        
        print("   ✅ SQLite database: streamlit_research_database.db")
        print("   ✅ CSV files: streamlit_nodes.csv, streamlit_edges.csv, streamlit_summary.csv")
        print("   ✅ JSON backup: streamlit_database.json")

def main():
    """Generate enhanced database with realistic citation chains"""
    
    print("🚀 Starting Enhanced Database Generation...")
    print("Features: Temporal layers + Bridge papers + Selective chains\\n")
    
    # Initialize generator with seed for reproducibility
    generator = EnhancedStreamlitDatabaseGenerator(seed=42)
    
    # Generate complete database
    nodes_df, edges_df, summary_df = generator.generate_complete_database()
    
    # Save in multiple formats
    generator.save_for_streamlit(nodes_df, edges_df, summary_df)
    
    print("\\n🎉 Enhanced Database Generation Complete!")
    print("Ready for Streamlit with realistic citation chains and temporal layers.")

if __name__ == "__main__":
    main()
