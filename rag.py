import os
import faiss
import numpy as np

from openai import OpenAI
from dotenv import load_dotenv

from knowledge_base import documents

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def chunk_documents(documents):
    chunks = []

    for doc in documents:
        paragraphs = doc.strip().split("\n\n")

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if paragraph:
                chunks.append(paragraph)

    return chunks


chunks = chunk_documents(documents)

def get_embedding(text):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding

embeddings = []

for chunk in chunks:
    embeddings.append(get_embedding(chunk))

embedding_matrix = np.array(embeddings).astype("float32")

index = faiss.IndexFlatL2(embedding_matrix.shape[1])

index.add(embedding_matrix)

def retrieve_documents(query, top_k=4):

    query_embedding = np.array(
        [get_embedding(query)],
        dtype="float32"
    )

  
    distances, indices = index.search(query_embedding, top_k)

    results = []

    for i in indices[0]:
        results.append(chunks[i])

    return results