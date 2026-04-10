import os
from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv

# Load env variables from root .env
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path)

class PineconeService:
    def __init__(self, index_name: str = "glow-rag-index", dimension: int = 1536):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not self.pinecone_api_key or self.pinecone_api_key == "your_pinecone_api_key_here":
            print("WARNING: PINECONE_API_KEY is not set or placeholder is used. VectorDB won't work correctly.")
        
        self.index_name = index_name
        self.dimension = dimension
        
        self.pc = Pinecone(api_key=self.pinecone_api_key) if self.pinecone_api_key else None
        
        self.serpapi_endpoint = os.getenv("SERPAPI_BASE_URL")
        self.serpapi_api_key = os.getenv("SERPAPI_API_KEY")

        # Setup standard OpenAI client acting as SerpAPI endpoint fallback
        if self.serpapi_endpoint and self.serpapi_api_key:
            self.openai_client = OpenAI(
                api_key=self.serpapi_api_key,
                base_url=self.serpapi_endpoint
            )
            self.deployment_name = "text-embedding-3-small" # Generic embedding model for external apis
            self.is_azure = False
        else:
            self.openai_client = None
            print("WARNING: No SERPAPI OpenAI API keys found. Embeddings will fail.")

        # Ensure index exists
        if self.pc:
            self._ensure_index()
            self.index = self.pc.Index(self.index_name)

    def _ensure_index(self):
        """Creates the Pinecone index if it doesn't already exist."""
        existing_indexes = [idx["name"] for idx in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            print(f"Creating Pinecone index: '{self.index_name}'...")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        else:
            print(f"Pinecone index '{self.index_name}' already exists.")

    def embed_text(self, text: str) -> List[float]:
        """Generates an embedding for the given text."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized.")
        
        try:
            if self.is_azure:
                response = self.openai_client.embeddings.create(
                    input=text,
                    model=self.deployment_name
                )
            else:
                response = self.openai_client.embeddings.create(
                    input=text,
                    model=self.deployment_name
                )
            return response.data[0].embedding
        except Exception as e:
            if "DeploymentNotFound" in str(e):
                print(f"AZURE OPENAI CONFIG ERROR: Deployment '{self.deployment_name}' not found.")
                print("Please update the 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT' variable in your .env file with your actual Azure embedding deployment name.")
            else:
                print(f"Error generating embedding: {e}")
            raise

    def upsert_data(self, chunks: List[Dict]):
        """
        Upserts chunked data to Pinecone. 
        Expects chunks format: [{'id': '..', 'text': '..', 'metadata': {..}}, ...]
        """
        if not self.pc:
            print("Skipping upsert: Pinecone client not initialized.")
            return

        upsert_payload = []
        for chunk in chunks:
            text = chunk.get("text", "")
            if not text:
                continue
            
            embedding = self.embed_text(text)
            
            # Combine original metadata + the raw text for retrieval reference
            metadata = chunk.get("metadata", {})
            metadata["text"] = text 

            upsert_payload.append({
                "id": chunk["id"],
                "values": embedding,
                "metadata": metadata
            })

        print(f"Upserting {len(upsert_payload)} vectors to index '{self.index_name}'...")
        self.index.upsert(vectors=upsert_payload)
        print("Upsert complete.")

    def query_similar_data(self, query: str, top_k: int = 3) -> List[Dict]:
        """Queries the vector database for text similar to the query."""
        if not self.pc:
            print("Skipping query: Pinecone client not initialized.")
            return []

        query_embedding = self.embed_text(query)
        
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        matches = []
        for match in results.get("matches", []):
            matches.append({
                "id": match.get("id"),
                "score": match.get("score"),
                "text": match.get("metadata", {}).get("text", ""),
                "section": match.get("metadata", {}).get("section", "")
            })
        return matches

if __name__ == "__main__":
    # Test script formatSSS
    from .data_parser import parse_glow_data
    
    rag_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'RAG', 'Glow_Rag.json'))
    try:
        service = PineconeService()
        print("Parsing data...")
        chunks = parse_glow_data(rag_file)
        
        if service.pc:
            print("Upserting data...")
            service.upsert_data(chunks)
            
            print("Testing Query...")
            res = service.query_similar_data("What are the key ingredients?")
            for r in res:
                print(f"--- Score: {r['score']} ---")
                print(r['text'][:200] + "...")
    except Exception as e:
        print(f"Script aborted: {e}")
