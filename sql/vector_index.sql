-- Create a vector index on the EMBEDDING column of the AI_DOCS table; is used in load_embeddings.sql in search_ai_docs
ALTER SESSION SET CURRENT_SCHEMA=APP_OWNER;
BEGIN
  DBMS_VECTOR.CREATE_INDEX(
    'AI_DOCS_EMB_HNSW',         -- idx_name
    'AI_DOCS',                  -- table_name
    'EMBEDDING',                -- idx_vector_col
    NULL,                       -- idx_include_cols
    NULL,                       -- idx_partitioning_scheme (defaults to GLOBAL)
    'INMEMORY NEIGHBOR GRAPH',  -- idx_organization for HNSW
    'COSINE',                   -- idx_distance_metric (or other)
    90,                         -- idx_accuracy
    '{"type":"HNSW","neighbors":16,"efConstruction":200}', -- idx_parameters JSON
    1                           -- idx_parallel_creation
  );
END;
/


SELECT id, dealership_id
FROM   ai_docs
ORDER  BY VECTOR_DISTANCE(embedding, :query_vec, COSINE)
FETCH FIRST 10 ROWS ONLY;