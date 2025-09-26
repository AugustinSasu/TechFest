-- To view info about the space allocation for Vector Pool;
-- Until an HNSW index is created, V$VECTOR_MEMORY_POOL shows 0 in the ALLOC_BYTES column.
SELECT CON_ID, POOL, ALLOC_BYTES/1024/1024 AS ALLOC_MB, USED_BYTES/1024/1024 AS USED_MB, POPULATE_STATUS
FROM V$VECTOR_MEMORY_POOL;

SELECT ISPDB_MODIFIABLE FROM V$SYSTEM_PARAMETER WHERE NAME = 'vector_memory_size';

-- parameter that adjust Vector Pool size
-- initially is 0 for CDB$ROOT and for PDBs
-- needs to be set in CDB$ROOT first, optionally in PDB
SHOW PARAMETER vector_memory_size;


-- for PDB is 0 if not allocated
-- for CDB is 1536M (for Oracle 23ai Free Release)
SHOW PARAMETER sga_target;


-- first allocate vector pool memory in CDB
ALTER SESSION SET CONTAINER = CDB$ROOT;
-- use SCOPE = SPFILE because vector_memory_size = 0 and cannot change dynamically which SCOPE = BOTH tries to do
-- SPFILE - Server Permanent File -- Change is written here; It does not affect the current instance; needs restart
-- BOTH - Change applies immediately in memory and is saved to the SPFILE - doesn't work here!
ALTER SYSTEM SET VECTOR_MEMORY_SIZE = 100M SCOPE = SPFILE;

-- restart to pick up the change
SHUTDOWN IMMEDIATE;
STARTUP;


ALTER SESSION SET CONTAINER = CDB$ROOT;

-- now SCOPE = BOTH works because vector_memory_size is not 0 anymore; it's 100M
ALTER SYSTEM SET VECTOR_MEMORY_SIZE = 500M SCOPE = BOTH;

-- ALTERNATIVE: set VECTOR_MEMORY_SIZE to 1 => auto-grow mode - needs SCOPE=SPFILE
-- Warning: in Oracle 23ai Free can raise errors due to limited memory

-- ALTER SYSTEM SET VECTOR_MEMORY_SIZE = 1 SCOPE=SPFILE;
-- SHUTDOWN IMMEDIATE;
-- STARTUP;


--returns the current container
SELECT SYS_CONTEXT('USERENV', 'CON_NAME') AS current_container FROM dual; 

 --lists all containers
SELECT CON_ID, NAME, OPEN_MODE FROM V$CONTAINERS;


ALTER SESSION SET CONTAINER = FREEPDB1;

-- (OPTIONAL) WHEN CDB is FIXED:
-- Allocate SGA_TARGET for FREEPDB1; but without SGA_TARGET set in FREEPDB1, Oracle will allocate memory from CDB's SGA_TARGET

-- allocate SGA_TARGET for FREEPDB1 from CDB's SGA_TARGET
-- ALTER SYSTEM SET SGA_TARGET = 512M SCOPE = BOTH;

-- allocate vector_memory_size for FREEPDB1 (maximum 70% of SGA_TARGET)
-- ALTER SYSTEM SET VECTOR_MEMORY_SIZE = 256M SCOPE = BOTH;



-- the index must be created in APP_OWNER schema
ALTER SESSION SET CURRENT_SCHEMA=APP_OWNER;

-- Create HNSW index on ai_docs.embedding
BEGIN
  DBMS_VECTOR.CREATE_INDEX(
    idx_name                => 'AI_DOCS_EMB_HNSW',
    table_name              => 'AI_DOCS',
    idx_vector_col          => 'EMBEDDING',
    idx_include_cols        => NULL,
    idx_partitioning_scheme => NULL,
    idx_organization        => 'INMEMORY NEIGHBOR GRAPH',
    idx_distance_metric     => 'COSINE',
    idx_accuracy            => 90,
    idx_parameters          => '{"type":"HNSW","neighbors":4,"efConstruction":64}',
    idx_parallel_creation   => 1
  );
END;
/


-- Check index status
SELECT index_name, table_name, status, index_type
FROM   all_indexes -- or user_indexes if connected as the schema owner
WHERE  index_name = 'AI_DOCS_EMB_HNSW';


--To see the estimated index memory to be allocated:
SET SERVEROUTPUT ON;

DECLARE
  response_clob CLOB;
BEGIN
  DBMS_VECTOR.INDEX_VECTOR_MEMORY_ADVISOR(
    INDEX_TYPE     => 'HNSW',
    NUM_VECTORS    => 100000, -- adjust based on your data
    DIM_COUNT      => 1024,   -- your embedding size
    DIM_TYPE       => 'FLOAT32',
    PARAMETER_JSON => '{"neighbors":16,"efConstruction":200}',
    RESPONSE_JSON  => response_clob
  );
  DBMS_OUTPUT.PUT_LINE(response_clob);
END;
/

COMMIT;