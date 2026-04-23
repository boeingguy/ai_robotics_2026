-- =====================================================
-- Query 2: Graph Traversal using Apache AGE
-- Find reachable places containing specific object classes
-- =====================================================

SELECT * FROM cypher('semantic_maze_graph', $$
    MATCH (o:Object)-[:LOCATED_IN]->(p:Place)
    WHERE o.class_label IN ['cup', 'chair', 'table']
    RETURN p.place_id, p.name, count(o) as object_count
    ORDER BY object_count DESC
$$) as (place_id agtype, name agtype, object_count agtype);
