import chromadb
from sentence_transformers import SentenceTransformer

# 1. ጠንካራ የሆነ Multilingual ሞዴል መጠቀም
print("ሞዴሉ እየተዘጋጀ ነው...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 2. ዳታውን ትርጉም ባለው መልኩ ማዘጋጀት (አማርኛ + እንግሊዝኛ ጎን ለጎን)
# ይህ ሞዴሉ ትርጉሙን ይበልጥ እንዲረዳው ይረዳዋል
documents = [
    "የቤት ብድር ለማግኘት 20% ቅድመ ክፍያ ያስፈልጋል። Home loan requires 20 percent down payment",
    "የመኪና ብድር ወለድ በዓመት 15% ነው። Car loan interest rate is 15 percent per year",
    "አዲስ አካውንት ለመክፈት የታደሰ መታወቂያ ያስፈልጋል። Opening a new account requires a valid ID"
]

# 3. ChromaDB (ሁልጊዜ አዲስ እንዲሆን ስሙን እንቀይር)
print("ዳታቤዙ እየተፈጠረ ነው...")
client = chromadb.Client()
# በየሙከራው ስም መቀየር ግጭትን ያስወግዳል
collection = client.create_collection(name="bank_final_test")

embeddings = model.encode(documents).tolist()

collection.add(
    embeddings=embeddings,
    documents=documents,
    ids=["id1", "id2", "id3"]
)

# 4. መፈለግ
print("-" * 30)
# ጥያቄውንም አማርኛ + እንግሊዝኛ ብናደርገው ይበልጥ ይረዳል
query_text = "ቤት መግዣ ገንዘብ እንዴት አገኛለሁ? How can I get money to buy a house?"
print(f"ጥያቄ፦ {query_text}")

query_embedding = model.encode([query_text]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=1
)

print(f"የተገኘ መልስ፦ {results['documents'][0][0]}")
print("-" * 30)