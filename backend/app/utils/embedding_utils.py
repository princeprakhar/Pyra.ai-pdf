from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from chonkie import SemanticChunker
from pinecone.grpc import PineconeGRPC as Pinecone
from app.config import OPENAI_API_KEY, PINECONE_API_KEY

embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vector_store = Chroma(embedding_function=embeddings)
chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-8M",
    threshold=0.5,
    chunk_size=512,
    min_sentences=1
)
pc = Pinecone(
    api_key=PINECONE_API_KEY,
    pool_threads=30,
    ssl_verify=False
)
index_name = 'document-rag'
