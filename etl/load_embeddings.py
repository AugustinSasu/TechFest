import os
import numpy as np
import oracledb
import pandas as pd

DB_USER = os.getenv("DB_USER", "APP_OWNER")
DB_PASS = os.getenv("DB_PASS", "App#Pass3")
DB_DSN  = os.getenv("DB_DSN",  "localhost:1521/FREEPDB1")  # host:port/service

VECTOR_DIM = 1536  # match your model

def embed(text: str) -> np.ndarray:
    # TODO: replace with your embedding provider call
    # Must return np.float32 of shape (VECTOR_DIM,)
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    return rng.random(VECTOR_DIM, dtype=np.float32)

def main():
    # Example ETL input (use your real source instead of this DataFrame)
    df = pd.DataFrame([
        {"dealership_id": 1, "src_text": "Lead asked for a VW Golf test drive."},
        {"dealership_id": 1, "src_text": "Customer negotiated price on Tiguan."},
    ])

    # Connect (thin mode)
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    cur = conn.cursor()

    # Seed dealership if needed
    cur.execute("MERGE INTO dealership d USING (SELECT :1 name FROM dual) s ON (d.name = s.name) "
                "WHEN NOT MATCHED THEN INSERT (name) VALUES (s.name)",
                ["Demo VW Dealership"])
    conn.commit()

    # Insert texts + embeddings
    sql = """INSERT INTO ai_docs (dealership_id, src_text, embedding)
             VALUES (:1, :2, :3)"""
    rows = []
    for _, r in df.iterrows():
        vec = embed(r["src_text"])
        rows.append((int(r["dealership_id"]), r["src_text"], vec))

    cur.executemany(sql, rows)
    conn.commit()

    # Sample similarity query (cosine)
    qvec = embed("Book a test drive for Golf")
    cur.execute(
        """SELECT id, dealership_id, SUBSTR(src_text,1,60) snippet
             FROM ai_docs
            ORDER BY VECTOR_DISTANCE(embedding, :qvec, COSINE)
            FETCH FIRST 5 ROWS ONLY""",
        qvec)
    for id_, d_id, snip in cur.fetchall():
        print(id_, d_id, snip)

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
