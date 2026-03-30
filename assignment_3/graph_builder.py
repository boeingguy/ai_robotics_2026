class GraphBuilder:
    def __init__(self, epsilon=1.5):
        self.epsilon = epsilon
        self.places = {} # {place_id: [poses]}
        self.place_counter = 0

    def update_topology(self, x, y, det_id):
        """Online DBSCAN logic: Cluster poses into Places"""
        assigned_place = None
        
        # Check proximity to existing Place centroids
        for p_id, poses in self.places.items():
            centroid = np.mean(poses, axis=0)
            if hypot(x - centroid, y - centroid) < self.epsilon:
                assigned_place = p_id
                self.places[p_id].append((x, y))
                break
        
        if not assigned_place:
            self.place_counter += 1
            assigned_place = f"place_{self.place_counter}"
            self.places[assigned_place] = [(x, y)]

        # Conceptual Cypher for AGE
        print(f"CYPHER: MATCH (o:Observation {{det_id: '{det_id}'}})")
        print(f"        MERGE (p:Place {{id: '{assigned_place}'}})")
        print(f"        CREATE (o)-[:PART_OF]->(p)")
        return assigned_place

gb = GraphBuilder()
print(f"Assigned to: {gb.update_topology(1.0, 1.0, 'run1_kf1_red_block')}")
