from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from qdrant_client import QdrantClient, models
import os
from openai import OpenAI
from dotenv import load_dotenv
from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

# --- Configuration & Initialization ---

@lru_cache()
def get_settings():
    """Loads settings from environment variables. Uses lru_cache for performance."""
    load_dotenv()
    settings = {
        "qdrant_host": os.getenv("QDRANT_URL"),
        "qdrant_api_key": os.getenv("QDRANT_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "collection_name": "propertiesV3",
        "supabase_url": os.getenv("SUPABASE_URL"),
        "supabase_key": os.getenv("SUPABASE_KEY")
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
# Define the specific origins that are allowed to make requests.
allowed_origins = [
    "http://localhost:3000",          # For local development
    "https://showtimeprop.com",       # Your main production domain
    "https://www.showtimeprop.com",   # Your www production domain
    "https://bnicolini.showtimeprop.com" # Your tenant subdomain
    # Add other tenant subdomains here as they are created, or use a wildcard pattern
    # For wildcard subdomains, you might need allow_origin_regex in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Tenant Resolution Middleware ---
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    host = request.headers.get("host", "").split(":")[0]
    prod_base_domain = "showtimeprop.com"
    api_host = f"fapi.{prod_base_domain}"
    subdomain = None

    # We only resolve tenants for hosts that are NOT the main API host
    if host.endswith(prod_base_domain) and host != api_host:
        subdomain = host.split(f".{prod_base_domain}")[0]
    # Also handle localhost subdomains for local tenant testing
    elif host.endswith(".localhost"):
        subdomain = host.split('.')[0]

    tenant_id = None
    if subdomain:
        try:
            # If there's a subdomain, we MUST find a matching tenant
            response = supabase_cli.table("tenants").select("id").eq("subdomain", subdomain).single().execute()
            if not response.data:
                # Use a more specific error for debugging
                return Response(content=f'{{"detail":"Tenant with subdomain \'{subdomain}\' not found."}}', status_code=404, media_type="application/json")
            
            tenant_id = response.data['id']
        except Exception as e:
            print(f"Error during tenant resolution: {e}")
            return Response(content='{"detail":"Error resolving tenant."}', status_code=500, media_type="application/json")

    request.state.tenant_id = tenant_id # This will be the UUID or None
    
    response = await call_next(request)
    return response

# Initialize clients
try:
    qdrant_cli = QdrantClient(url=settings["qdrant_host"], api_key=settings["qdrant_api_key"])
    openai_cli = OpenAI(api_key=settings["openai_api_key"])
    supabase_cli: Client = create_client(settings["supabase_url"], settings["supabase_key"])
    
    qdrant_cli.get_collection(collection_name=settings["collection_name"])
except Exception as e:
    raise RuntimeError(f"Failed to initialize clients or connect to services: {e}")


# --- Pydantic Models ---
class SearchRequestModel(BaseModel):
    query: str
    filters: dict = None
    top_k: int = 5

# --- API Endpoints ---

@app.get("/test-tenant", summary="Test Tenant Resolution")
def test_tenant_resolution(request: Request):
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    return {"message": f"Request received successfully for tenant ID: {tenant_id}"}


@app.get("/properties/all", summary="Get All Properties")
def get_all_properties(request: Request):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    scroll_filter = None
    if tenant_id:
        print(f"Fetching all properties for tenant: {tenant_id}")
        scroll_filter = models.Filter(
            must=[models.FieldCondition(key="tenant_id", match=models.MatchValue(value=tenant_id))]
        )
    else:
        print("Fetching all properties without tenant filter.")

    try:
        results, _ = qdrant_cli.scroll(
            collection_name=settings["collection_name"],
            limit=1000,
            with_payload=True,
            with_vectors=False,
            scroll_filter=scroll_filter # Pass the filter here (can be None)
        )
        return [record.payload for record in results]
    except Exception as e:
        print(f"Error retrieving all properties: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve properties from the database.")


@app.post("/search", summary="Semantic Property Search")
def search(request: Request, search_request: SearchRequestModel):
    tenant_id = getattr(request.state, "tenant_id", None)

    if not tenant_id:
        # For now, block searches on the main domain without a tenant context
        # In the future, this could search public properties or similar
        raise HTTPException(status_code=400, detail="Search requires a tenant context. Please use a subdomain.")

    print(f"Performing search for tenant: {tenant_id}")
    try:
        embedding_response = openai_cli.embeddings.create(
            input=search_request.query,
            model="text-embedding-3-small"
        )
        query_vector = embedding_response.data[0].embedding

        conditions = []
        if search_request.filters:
            for field, value in search_request.filters.items():
                conditions.append(models.FieldCondition(
                    key=field,
                    match=models.MatchValue(value=value)
                ))
        
        conditions.append(models.FieldCondition(key="tenant_id", match=models.MatchValue(value=tenant_id)))
        
        query_filter = models.Filter(must=conditions) if conditions else None

        hits = qdrant_cli.search(
            collection_name=settings["collection_name"],
            query_vector=query_vector,
            limit=search_request.top_k,
            query_filter=query_filter,
            search_params=models.SearchParams(hnsw_ef=128, exact=False),
        )

        return [hit.payload for hit in hits]
    except Exception as e:
        print(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 