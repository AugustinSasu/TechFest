import os
import numpy as np
import oracledb
import pandas as pd
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# DB connection paramameters
DB_USER = os.getenv("DB_USER", "APP_OWNER")
DB_PASS = os.getenv("DB_PASS", "app_owner")
DB_DSN  = os.getenv("DB_DSN",  "localhost:1521/FREEPDB1")  # host:port/service

VECTOR_DIM = 1536  # adjust to the model in use

def embed(text: str) -> np.ndarray:
    response = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    vec = response.data[0].embedding
    return np.array(vec, dtype=np.float32)

def main():
    # connecting to the DB
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    cur = conn.cursor()

    # extract unembedded texts
    df = pd.read_sql("""
        SELECT id, dealership_id, src_text
        FROM ai_raw_input
        WHERE is_embedded = 'N'
        FETCH FIRST 100 ROWS ONLY
    """, conn)

    if df.empty:
        print("No new input texts to embed.")
        return

    # the querry to execute
    insert_sql = """INSERT INTO ai_docs (dealership_id, src_text, embedding)
             VALUES (:1, :2, :3)"""


    # building the new rows with embeddings
    rows = []
    ids_to_update = []
    for _, row in df.iterrows():
        vec = embed(row["src_text"])
        rows.append((int(row["dealership_id"]), row["src_text"], vec))
        ids_to_update.append(int(row["id"]))


    # executing the insert with the new rows
    cur.executemany(insert_sql, rows)

    # setting the is_embedded flag to 'Y' for processed rows
    cur.executemany(
        "UPDATE ai_raw_input SET is_embedded = 'Y' WHERE id = :1",
        [(i,) for i in ids_to_update]
    )

    conn.commit()
    print(f"Embedded and stored {len(rows)} rows.")

    cur.close()
    conn.close()

# searching within ai_docs; easier query using VECTOR_DISTANCE
def search_ai_docs(query_text: str, dealership_id: int = None, top_n: int = 5):
    """Run a semantic search against ai_docs using VECTOR_DISTANCE"""
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    cur = conn.cursor()

    qvec = embed(query_text)

    # Optional filter by dealership
    where_clause = "WHERE dealership_id = :dealer_id" if dealership_id else ""
    sql = f"""
        SELECT id, dealership_id, SUBSTR(src_text, 1, 100) AS snippet
        FROM ai_docs
        {where_clause}
        ORDER BY VECTOR_DISTANCE(embedding, :qvec, COSINE) 
        FETCH FIRST :n ROWS ONLY
    """

    params = {
        "qvec": qvec.tolist(),
        "n": top_n
    }
    if dealership_id:
        params["dealer_id"] = dealership_id

    cur.execute(sql, params)
    results = cur.fetchall()

    cur.close()
    conn.close()
    return results

if __name__ == "__main__":
    main()
