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
