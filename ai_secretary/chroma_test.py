import chromadb
from chromadb.config import Settings

# Conectare la baza ta locală Chroma
client = chromadb.PersistentClient(path="./chroma_db", settings=Settings(allow_reset=True))

# Ia colecția "sales"
col = client.get_or_create_collection("sales")

# Vezi câte documente are
print("Total documente în colecție:", col.count())

# Afișează primele 5 rânduri (metadate)
res = col.get(include=["metadatas"], limit=5)
for i, m in enumerate(res["metadatas"], 1):
    print(f"{i}.", m)
