import aiohttp
from fastapi import HTTPException
from app.config import JINA_API_KEY

async def rerank_documents(query: str, documents: list):
    url = 'https://api.jina.ai/v1/rerank'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {JINA_API_KEY}",
        'User-Agent': 'RAGSystem/1.0'
    }
    data = {
        "model": "jina-reranker-v2-base-multilingual",
        "query": query,
        "top_n": 3,
        "documents": documents
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data, ssl=False) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Reranking failed")
            return (await response.json())['results']
