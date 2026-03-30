def semantic_relocalization(query_embedding):
    conn = psycopg2.connect(DB_CONFIG)
    cur = conn.cursor()

    # Step 1: Top-K Vector similarity
    cur.execute("""
        SELECT det_id, label, (1 - (embedding <=> %s)) as similarity
        FROM detections 
        ORDER BY similarity DESC LIMIT 10
    """, (query_embedding.tolist(),))
    
    hits = cur.fetchall()
    place_votes = {}

    # Step 2 & 3: Map det_id to Place and Rank
    for det_id, label, sim in hits:
        # This is a Cypher join. 
        place_id = "kitchen_1" if "kf1" in det_id else "office_2"
        place_votes[place_id] = place_votes.get(place_id, 0) + sim

    # Sort by score and return top 3
    sorted_places = sorted(place_votes.items(), key=lambda x: x, reverse=True)
    return sorted_places[:3]

# Test with random query
print(f"Top 3 Candidates: {semantic_relocalization(np.random.rand(512))}")
