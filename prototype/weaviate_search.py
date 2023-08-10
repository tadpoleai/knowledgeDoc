#!pip install weaviate-client

import weaviate
import os

from langchain.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from langchain.schema import Document
from langchain.vectorstores import VectorStore

class HybridSearchByWeaviate():
    def __init__(self) -> None:
        
        WEAVIATE_URL = os.getenv("WEAVIATE_URL")
        print(f'WEAVIATE_URL:{WEAVIATE_URL}')
        client = weaviate.Client(
            url=WEAVIATE_URL,
            auth_client_secret=weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY")),
            additional_headers={
                "X-Openai-Api-Key": os.getenv("OPENAI_API_KEY"),
            },
        )
        self.retriever = WeaviateHybridSearchRetriever(client, index_name="LangChain", text_key="text")
        
        pass
    
    def as_retriever(self):
        return self.retriever
    
    def ingest_docments(self, docs:list[Document]):
        self.retriever.add_documents(docs)
        pass
    
    def search(self, query:str):
        result = self.retriever.get_relevant_documents(query)
        
        return result
    
