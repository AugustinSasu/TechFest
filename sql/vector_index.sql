-- Create a vector index on the EMBEDDING column of the AI_DOCS table
BEGIN
  DBMS_VECTOR.CREATE_INDEX(
    index_name    => 'AI_DOCS_EMB_HNSW',   -- name of the index
    schema_name   => 'APP_OWNER',          -- schema where table lives
    table_name    => 'AI_DOCS',            -- table with the embeddings
    column_name   => 'EMBEDDING',          -- VECTOR column
    index_type    => 'HNSW'                -- ANN algorithm (HNSW or IVF)
  );
END;
/
