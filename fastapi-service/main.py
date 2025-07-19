from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient, models
import os
from openai import OpenAI
from dotenv import load_dotenv
from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration & Initialization ---

@lru_cache()
def get_settings():
    """Loads settings from environment variables. Uses lru_cache for performance."""
    load_dotenv()
    settings = {
        "qdrant_host": os.getenv("QDRANT_URL"),
        "qdrant_api_key": os.getenv("QDRANT_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "collection_name": "propertiesV3"
    }
    for key, value in settings.items():
        if not value:
            raise RuntimeError(f"{key.upper()} is not set in environment variables.")
    return settings

settings = get_settings()

app = FastAPI(
    title="Real Estate API",
    description="API to search and retrieve property data from Qdrant.",
    version="1.0.0"
)

# --- Add CORS Middleware ---
# This allows your frontend (localhost:3000) to make requests to this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can be more specific in production e.g., ["http://localhost:3000", "https://your-prod-domain.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize clients
try:
    qdrant_cli = QdrantClient(url=settings["qdrant_host"], api_key=settings["qdrant_api_key"])
    openai_cli = OpenAI(api_key=settings["openai_api_key"])
    # Check if collection exists
    qdrant_cli.get_collection(collection_name=settings["collection_name"])
except Exception as e:
    raise RuntimeError(f"Failed to initialize clients or connect to Qdrant collection: {e}")


# --- Pydantic Models ---

class SearchRequestModel(BaseModel):
    query: str
    filters: dict = None
    top_k: int = 5


# --- API Endpoints ---

@app.get("/properties/all", summary="Get All Properties")
def get_all_properties():
    """
    Retrieves all properties from the Qdrant collection.
    This is optimized for fetching data to display on a map.
    """
    try:
        # Scroll is the efficient way to retrieve all points.
        # We disable vectors as they are not needed for the map view.
        results, _ = qdrant_cli.scroll(
            collection_name=settings["collection_name"],
            limit=1000,  # Adjust if you have more than 1000 properties
            with_payload=True,
            with_vectors=False,
        )
        return [record.payload for record in results]
    except Exception as e:
        # Log the exception for debugging
        print(f"Error retrieving all properties: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve properties from the database.")


@app.post("/search", summary="Semantic Property Search")
def search(request: SearchRequestModel):
    """
    Performs semantic search for properties based on a text query.
    """
    try:
        # 1. Get embedding from OpenAI (using new SDK)
        embedding_response = openai_cli.embeddings.create(
            input=request.query,
            model="text-embedding-3-small"
        )
        query_vector = embedding_response.data[0].embedding

        # 2. Build optional filter
        conditions = []
        if request.filters:
            for field, value in request.filters.items():
                conditions.append(models.FieldCondition(
                    key=field,
                    match=models.MatchValue(value=value)
                ))
        query_filter = models.Filter(must=conditions) if conditions else None

        # 3. Perform search in Qdrant
        hits = qdrant_cli.search(
            collection_name=settings["collection_name"],
            query_vector=query_vector,
            limit=request.top_k,
            query_filter=query_filter,
            search_params=models.SearchParams(hnsw_ef=128, exact=False),
        )

        return [hit.payload for hit in hits]
    except Exception as e:
        print(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 