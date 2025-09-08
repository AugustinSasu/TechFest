from flask import Flask, request, jsonify
import os
import numpy as np
import oracledb
import openai

# --- Config ---
DB_USER = os.getenv("DB_USER", "APP_OWNER")
DB_PASS = os.getenv("DB_PASS", "app_owner")
DB_DSN = os.getenv("DB_DSN", "localhost:1521/FREEPDB1")
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# --- Embedding Function ---
def embed(text: str) -> np.ndarray:
    response = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    vec = response.data[0].embedding
    return np.array(vec, dtype=np.float32)

# --- Semantic Search Endpoint ---
@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query_text = data.get("query")
    dealership_id = data.get("dealership_id")
    top_n = data.get("top_n", 5)

    if not query_text:
        return jsonify({"error": "Query text is required."}), 400

    qvec = embed(query_text)

    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    cur = conn.cursor()

    where_clause = "WHERE dealership_id = :dealer_id" if dealership_id else ""
    sql = f"""
        SELECT id, dealership_id, SUBSTR(src_text, 1, 100) AS snippet
        FROM ai_docs
        {where_clause}
        ORDER BY VECTOR_DISTANCE(embedding, :qvec, COSINE)
        FETCH FIRST :n ROWS ONLY
    """

    params = {"qvec": qvec.tolist(), "n": top_n}
    if dealership_id:
        params["dealer_id"] = dealership_id

    cur.execute(sql, params)
    results = [
        {"id": row[0], "dealership_id": row[1], "snippet": row[2]}
        for row in cur.fetchall()
    ]

    cur.close()
    conn.close()

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
