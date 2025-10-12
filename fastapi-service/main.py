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
    "https://*.vercel.app",  # Permitir todos los subdominios de Vercel
    "https://properties-nuxt.vercel.app",  # URL de producción específica
    "https://www.showtimeprop.com",   # Your www production domain
    "https://bnicolini.showtimeprop.com" # Your tenant subdomains
    # Add other tenant subdomains here as they are created, or use a wildcard pattern
    # For wildcard subdomains, you might need allow_origin_regex in production
]
# Regex to allow any Vercel deployment URL
vercel_regex = r"https://.*-alex-nicolinis-projects\.vercel\.app"


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=vercel_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Tenant Resolution Middleware ---
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    # Determine the hostname of the service making the request.
    # Prefer the 'Origin' header for cross-domain requests (Vercel, localhost).
    # Fallback to 'Host' for direct API calls (curl, Postman).
    origin = request.headers.get("origin")
    host_header = request.headers.get("host", "")
    
    request_hostname = ""
    if origin:
        # Origin format: "https://subdomain.domain.com" -> we need "subdomain.domain.com"
        request_hostname = origin.split("://")[1].split(":")[0]
    else:
        request_hostname = host_header.split(":")[0]

    # --- Tenant Resolution Logic ---
    tenant_id = None
    subdomain = None
    prod_base_domain = "showtimeprop.com"
    api_host = f"fapi.{prod_base_domain}"

    # Don't try to resolve a tenant for Vercel preview URLs, localhost, or the API's own host
    if request_hostname.endswith('.vercel.app') or request_hostname == 'localhost' or request_hostname == api_host:
        print(f"Request from special source '{request_hostname}'. No tenant filter will be applied.")
        tenant_id = None
    # For production domains, extract the subdomain
    elif request_hostname.endswith(f".{prod_base_domain}"):
        # Extracts "bnicolini" from "bnicolini.showtimeprop.com"
        temp_subdomain = request_hostname.split(f".{prod_base_domain}")[0]
        # Avoid treating "www" or the main domain as a tenant
        if temp_subdomain and temp_subdomain != "www":
             subdomain = temp_subdomain

    # If we found a valid subdomain, get its ID from Supabase
    if subdomain:
        print(f"Found subdomain '{subdomain}'. Resolving tenant ID...")
        try:
            response = supabase_cli.table("tenants").select("id").eq("subdomain", subdomain).single().execute()
            if not response.data:
                return Response(content=f'{{"detail":"Tenant with subdomain \'{subdomain}\' not found."}}', status_code=404, media_type="application/json")
            
            tenant_id = response.data['id']
            print(f"Request mapped to tenant ID: {tenant_id}")
        except Exception as e:
            print(f"Error during tenant resolution for subdomain '{subdomain}': {e}")
            return Response(content='{"detail":"Error resolving tenant."}', status_code=500, media_type="application/json")

    # Attach tenant_id (or None) to the request state for use in endpoints
    request.state.tenant_id = tenant_id
    
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
    
    # NUEVA LÓGICA: Siempre mostrar todas las propiedades
    # El tenant_id se usa solo para identificar al realtor, no para filtrar propiedades
    print(f"Fetching all properties for tenant: {tenant_id} (all properties visible to all tenants)")

    try:
        results, _ = qdrant_cli.scroll(
            collection_name=settings["collection_name"],
            limit=1000,
            with_payload=True,
            with_vectors=False,
            scroll_filter=None  # No filter - show all properties
        )
        # --- DEBUGGING PRINT ---
        print(f"Qdrant query returned {len(results)} properties for tenant {tenant_id}.")
        # --- END DEBUGGING ---
        return [record.payload for record in results]
    except Exception as e:
        print(f"Error retrieving all properties: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve properties from the database.")


@app.post("/search", summary="Semantic Property Search")
def search(request: Request, search_request: SearchRequestModel):
    tenant_id = getattr(request.state, "tenant_id", None)

    # NUEVA LÓGICA: Permitir búsqueda sin tenant (mostrar todas las propiedades)
    print(f"Performing search for tenant: {tenant_id} (searching all properties)")
    
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
        
        # NO filtrar por tenant_id - buscar en todas las propiedades
        # conditions.append(models.FieldCondition(key="tenant_id", match=models.MatchValue(value=tenant_id)))
        
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


# --- ENDPOINTS DE FAVORITOS ---

@app.get("/favorites/{client_id}", summary="Get Client Favorites")
def get_client_favorites(request: Request, client_id: str):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        # Obtener favoritos del cliente para este tenant
        response = supabase_cli.table("favorites").select("*").eq("tenant_id", tenant_id).eq("client_id", client_id).execute()
        
        return {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "favorites": response.data
        }
    except Exception as e:
        print(f"Error retrieving favorites: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve favorites.")


@app.post("/favorites/{client_id}/{property_id}", summary="Add Property to Favorites")
def add_to_favorites(request: Request, client_id: str, property_id: str):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        # Verificar si ya existe
        existing = supabase_cli.table("favorites").select("*").eq("tenant_id", tenant_id).eq("client_id", client_id).eq("property_id", property_id).execute()
        
        if existing.data:
            return {"message": "Property already in favorites", "favorite": existing.data[0]}
        
        # Agregar a favoritos
        response = supabase_cli.table("favorites").insert({
            "tenant_id": tenant_id,
            "client_id": client_id,
            "property_id": property_id
        }).execute()
        
        return {"message": "Property added to favorites", "favorite": response.data[0]}
    except Exception as e:
        print(f"Error adding to favorites: {e}")
        raise HTTPException(status_code=500, detail="Could not add to favorites.")


@app.delete("/favorites/{client_id}/{property_id}", summary="Remove Property from Favorites")
def remove_from_favorites(request: Request, client_id: str, property_id: str):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        # Eliminar de favoritos
        response = supabase_cli.table("favorites").delete().eq("tenant_id", tenant_id).eq("client_id", client_id).eq("property_id", property_id).execute()
        
        return {"message": "Property removed from favorites", "deleted_count": len(response.data)}
    except Exception as e:
        print(f"Error removing from favorites: {e}")
        raise HTTPException(status_code=500, detail="Could not remove from favorites.")


@app.get("/favorites/tenant/{tenant_id}/clients", summary="Get All Clients for Tenant")
def get_tenant_clients(request: Request, tenant_id: str):
    # Verificar que el tenant_id coincida con el del request
    request_tenant_id = getattr(request.state, "tenant_id", None)
    
    if not request_tenant_id or str(request_tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied to this tenant's data.")
    
    try:
        # Obtener todos los clientes únicos para este tenant
        response = supabase_cli.table("favorites").select("client_id, created_at").eq("tenant_id", tenant_id).execute()
        
        # Agrupar por client_id y obtener el primer registro (fecha de registro)
        clients = {}
        for favorite in response.data:
            client_id = favorite["client_id"]
            if client_id not in clients:
                clients[client_id] = {
                    "client_id": client_id,
                    "first_activity": favorite["created_at"],
                    "favorites_count": 0
                }
            clients[client_id]["favorites_count"] += 1
        
        return {
            "tenant_id": tenant_id,
            "clients": list(clients.values())
        }
    except Exception as e:
        print(f"Error retrieving tenant clients: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve tenant clients.")


# --- ENDPOINTS DE USUARIOS/CLIENTES ---

@app.post("/users/register", summary="Register New Client")
def register_client(request: Request, user_data: dict):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        email = user_data.get("email")
        full_name = user_data.get("full_name")
        phone = user_data.get("phone")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required.")
        
        # Verificar si el usuario ya existe para este tenant
        existing = supabase_cli.table("users").select("*").eq("email", email).eq("tenant_id", tenant_id).execute()
        
        if existing.data:
            return {"message": "User already exists", "user": existing.data[0]}
        
        # Crear nuevo usuario
        response = supabase_cli.table("users").insert({
            "email": email,
            "full_name": full_name,
            "phone": phone,
            "tenant_id": tenant_id
        }).execute()
        
        return {"message": "User registered successfully", "user": response.data[0]}
    except Exception as e:
        print(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Could not register user.")


@app.get("/users/{user_id}", summary="Get User by ID")
def get_user(request: Request, user_id: str):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        response = supabase_cli.table("users").select("*").eq("id", user_id).eq("tenant_id", tenant_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found.")
        
        return {"user": response.data[0]}
    except Exception as e:
        print(f"Error retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve user.")


@app.get("/users/email/{email}", summary="Get User by Email")
def get_user_by_email(request: Request, email: str):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        response = supabase_cli.table("users").select("*").eq("email", email).eq("tenant_id", tenant_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found.")
        
        return {"user": response.data[0]}
    except Exception as e:
        print(f"Error retrieving user by email: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve user.")


@app.get("/users/tenant/{tenant_id}/all", summary="Get All Users for Tenant")
def get_tenant_users(request: Request, tenant_id: str):
    # Verificar que el tenant_id coincida con el del request
    request_tenant_id = getattr(request.state, "tenant_id", None)
    
    if not request_tenant_id or str(request_tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied to this tenant's data.")
    
    try:
        response = supabase_cli.table("users").select("*").eq("tenant_id", tenant_id).order("created_at", desc=True).execute()
        
        return {
            "tenant_id": tenant_id,
            "users": response.data,
            "total_count": len(response.data)
        }
    except Exception as e:
        print(f"Error retrieving tenant users: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve tenant users.")


@app.put("/users/{user_id}/update-login", summary="Update User Last Login")
def update_user_login(request: Request, user_id: str):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        response = supabase_cli.table("users").update({
            "last_login": "NOW()"
        }).eq("id", user_id).eq("tenant_id", tenant_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found.")
        
        return {"message": "Login time updated", "user": response.data[0]}
    except Exception as e:
        print(f"Error updating user login: {e}")
        raise HTTPException(status_code=500, detail="Could not update user login.")


# --- ENDPOINTS DE VISITAS Y CALIFICACIONES ---

@app.post("/visits/schedule", summary="Schedule Property Visit")
def schedule_visit(request: Request, visit_data: dict):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        client_id = visit_data.get("client_id")
        property_id = visit_data.get("property_id")
        visit_date = visit_data.get("visit_date")
        realtor_notes = visit_data.get("realtor_notes", "")
        
        if not all([client_id, property_id, visit_date]):
            raise HTTPException(status_code=400, detail="client_id, property_id, and visit_date are required.")
        
        # Verificar que el cliente pertenece al tenant
        client_check = supabase_cli.table("users").select("id").eq("id", client_id).eq("tenant_id", tenant_id).execute()
        if not client_check.data:
            raise HTTPException(status_code=404, detail="Client not found or not assigned to this tenant.")
        
        # Crear visita
        response = supabase_cli.table("visits").insert({
            "tenant_id": tenant_id,
            "client_id": client_id,
            "property_id": property_id,
            "visit_date": visit_date,
            "realtor_notes": realtor_notes,
            "visit_status": "scheduled"
        }).execute()
        
        return {"message": "Visit scheduled successfully", "visit": response.data[0]}
    except Exception as e:
        print(f"Error scheduling visit: {e}")
        raise HTTPException(status_code=500, detail="Could not schedule visit.")


@app.put("/visits/{visit_id}/complete", summary="Complete Visit with Rating")
def complete_visit(request: Request, visit_id: str, completion_data: dict):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        rating = completion_data.get("rating")
        client_notes = completion_data.get("client_notes", "")
        
        if not rating or rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")
        
        # Actualizar visita
        response = supabase_cli.table("visits").update({
            "visit_status": "completed",
            "rating": rating,
            "client_notes": client_notes,
            "updated_at": "NOW()"
        }).eq("id", visit_id).eq("tenant_id", tenant_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Visit not found.")
        
        return {"message": "Visit completed successfully", "visit": response.data[0]}
    except Exception as e:
        print(f"Error completing visit: {e}")
        raise HTTPException(status_code=500, detail="Could not complete visit.")


@app.get("/visits/client/{client_id}", summary="Get Client Visits")
def get_client_visits(request: Request, client_id: str):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        # Verificar que el cliente pertenece al tenant
        client_check = supabase_cli.table("users").select("id").eq("id", client_id).eq("tenant_id", tenant_id).execute()
        if not client_check.data:
            raise HTTPException(status_code=404, detail="Client not found or not assigned to this tenant.")
        
        # Obtener visitas del cliente
        response = supabase_cli.table("visits").select("*").eq("client_id", client_id).eq("tenant_id", tenant_id).order("visit_date", desc=True).execute()
        
        return {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "visits": response.data
        }
    except Exception as e:
        print(f"Error retrieving client visits: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve client visits.")


@app.get("/visits/tenant/{tenant_id}/all", summary="Get All Tenant Visits")
def get_tenant_visits(request: Request, tenant_id: str):
    # Verificar que el tenant_id coincida con el del request
    request_tenant_id = getattr(request.state, "tenant_id", None)
    
    if not request_tenant_id or str(request_tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied to this tenant's data.")
    
    try:
        # Obtener todas las visitas del tenant con información del cliente
        response = supabase_cli.table("visits").select("""
            *,
            users!inner(email, full_name, phone)
        """).eq("tenant_id", tenant_id).order("visit_date", desc=True).execute()
        
        return {
            "tenant_id": tenant_id,
            "visits": response.data,
            "total_count": len(response.data)
        }
    except Exception as e:
        print(f"Error retrieving tenant visits: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve tenant visits.")


@app.get("/visits/tenant/{tenant_id}/upcoming", summary="Get Upcoming Visits")
def get_upcoming_visits(request: Request, tenant_id: str):
    # Verificar que el tenant_id coincida con el del request
    request_tenant_id = getattr(request.state, "tenant_id", None)
    
    if not request_tenant_id or str(request_tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied to this tenant's data.")
    
    try:
        # Obtener visitas programadas (futuras)
        response = supabase_cli.table("visits").select("""
            *,
            users!inner(email, full_name, phone)
        """).eq("tenant_id", tenant_id).eq("visit_status", "scheduled").gte("visit_date", "NOW()").order("visit_date", desc=False).execute()
        
        return {
            "tenant_id": tenant_id,
            "upcoming_visits": response.data,
            "total_count": len(response.data)
        }
    except Exception as e:
        print(f"Error retrieving upcoming visits: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve upcoming visits.")


@app.post("/favorites/{client_id}/{property_id}/track", summary="Track Favorite Activity")
def track_favorite_activity(request: Request, client_id: str, property_id: str, activity_data: dict):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        action = activity_data.get("action", "viewed")  # 'added', 'removed', 'viewed'
        
        # Verificar que el cliente pertenece al tenant
        client_check = supabase_cli.table("users").select("id").eq("id", client_id).eq("tenant_id", tenant_id).execute()
        if not client_check.data:
            raise HTTPException(status_code=404, detail="Client not found or not assigned to this tenant.")
        
        # Registrar actividad
        response = supabase_cli.table("favorite_activity").insert({
            "tenant_id": tenant_id,
            "client_id": client_id,
            "property_id": property_id,
            "action": action
        }).execute()
        
        return {"message": "Activity tracked successfully", "activity": response.data[0]}
    except Exception as e:
        print(f"Error tracking favorite activity: {e}")
        raise HTTPException(status_code=500, detail="Could not track activity.")


@app.get("/clients/{client_id}/history", summary="Get Complete Client History")
def get_client_history(request: Request, client_id: str):
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    
    try:
        # Verificar que el cliente pertenece al tenant
        client_check = supabase_cli.table("users").select("id").eq("id", client_id).eq("tenant_id", tenant_id).execute()
        if not client_check.data:
            raise HTTPException(status_code=404, detail="Client not found or not assigned to this tenant.")
        
        # Obtener historial completo (favoritos + visitas)
        favorites_response = supabase_cli.table("favorite_activity").select("*").eq("client_id", client_id).eq("tenant_id", tenant_id).order("created_at", desc=True).execute()
        
        visits_response = supabase_cli.table("visits").select("*").eq("client_id", client_id).eq("tenant_id", tenant_id).order("visit_date", desc=True).execute()
        
        # Combinar y ordenar por fecha
        history = []
        
        # Agregar favoritos
        for favorite in favorites_response.data:
            history.append({
                "type": "favorite",
                "property_id": favorite["property_id"],
                "date": favorite["created_at"],
                "action": favorite["action"],
                "rating": None,
                "notes": None
            })
        
        # Agregar visitas
        for visit in visits_response.data:
            history.append({
                "type": "visit",
                "property_id": visit["property_id"],
                "date": visit["visit_date"],
                "action": visit["visit_status"],
                "rating": visit["rating"],
                "notes": visit["client_notes"] or visit["realtor_notes"]
            })
        
        # Ordenar por fecha descendente
        history.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "history": history,
            "total_activities": len(history)
        }
    except Exception as e:
        print(f"Error retrieving client history: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve client history.")

# =====================================================
# DASHBOARD ENDPOINTS FOR REALTORS
# =====================================================

@app.get("/dashboard/metrics/{realtor_id}")
async def get_realtor_metrics(realtor_id: str, request: Request):
    """Get dashboard metrics for a specific realtor."""
    try:
        tenant_id = request.state.tenant_id
        
        # Get Supabase client
        supabase_client = create_client(settings["supabase_url"], settings["supabase_key"])
        
        # Verify realtor belongs to tenant
        realtor_query = supabase_client.table("realtors").select("id").eq("id", realtor_id).eq("tenant_id", tenant_id).execute()
        if not realtor_query.data:
            raise HTTPException(status_code=404, detail="Realtor not found.")
        
        # Get metrics using the database function
        metrics_query = supabase_client.rpc("get_realtor_metrics", {
            "p_realtor_id": realtor_id,
            "p_date": "2024-01-15"  # You can make this dynamic
        }).execute()
        
        if metrics_query.data:
            metrics = metrics_query.data[0]
        else:
            metrics = {
                "total_leads": 0,
                "active_leads": 0,
                "converted_leads": 0,
                "revenue": 0
            }
        
        return {
            "realtor_id": realtor_id,
            "metrics": metrics,
            "date": "2024-01-15"
        }
    except Exception as e:
        print(f"Error retrieving realtor metrics: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve realtor metrics.")

@app.get("/dashboard/pipeline/{realtor_id}")
async def get_pipeline_data(realtor_id: str, request: Request):
    """Get pipeline data for a specific realtor."""
    try:
        tenant_id = request.state.tenant_id
        
        # Get Supabase client
        supabase_client = create_client(settings["supabase_url"], settings["supabase_key"])
        
        # Verify realtor belongs to tenant
        realtor_query = supabase_client.table("realtors").select("id").eq("id", realtor_id).eq("tenant_id", tenant_id).execute()
        if not realtor_query.data:
            raise HTTPException(status_code=404, detail="Realtor not found.")
        
        # Get pipeline data using the database function
        pipeline_query = supabase_client.rpc("get_leads_by_stage", {
            "p_realtor_id": realtor_id
        }).execute()
        
        # Get individual leads for each stage
        leads_query = supabase_client.table("lead_pipeline").select("""
            id,
            lead_id,
            stage,
            probability,
            estimated_value,
            last_activity,
            agent_leads!inner(id, name, email, phone)
        """).eq("realtor_id", realtor_id).execute()
        
        return {
            "realtor_id": realtor_id,
            "pipeline_summary": pipeline_query.data,
            "leads": leads_query.data
        }
    except Exception as e:
        print(f"Error retrieving pipeline data: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve pipeline data.")

@app.get("/dashboard/activities/{realtor_id}")
async def get_recent_activities(realtor_id: str, request: Request, limit: int = 10):
    """Get recent activities for a specific realtor."""
    try:
        tenant_id = request.state.tenant_id
        
        # Get Supabase client
        supabase_client = create_client(settings["supabase_url"], settings["supabase_key"])
        
        # Verify realtor belongs to tenant
        realtor_query = supabase_client.table("realtors").select("id").eq("id", realtor_id).eq("tenant_id", tenant_id).execute()
        if not realtor_query.data:
            raise HTTPException(status_code=404, detail="Realtor not found.")
        
        # Get recent activities using the database function
        activities_query = supabase_client.rpc("get_recent_activities", {
            "p_realtor_id": realtor_id,
            "p_limit": limit
        }).execute()
        
        return {
            "realtor_id": realtor_id,
            "activities": activities_query.data,
            "limit": limit
        }
    except Exception as e:
        print(f"Error retrieving recent activities: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve recent activities.")

@app.post("/dashboard/activities")
async def create_activity(activity_data: dict, request: Request):
    """Create a new activity for a realtor."""
    try:
        tenant_id = request.state.tenant_id
        realtor_id = activity_data.get("realtor_id")
        lead_id = activity_data.get("lead_id")
        
        # Get Supabase client
        supabase_client = create_client(settings["supabase_url"], settings["supabase_key"])
        
        # Verify realtor belongs to tenant
        realtor_query = supabase_client.table("realtors").select("id").eq("id", realtor_id).eq("tenant_id", tenant_id).execute()
        if not realtor_query.data:
            raise HTTPException(status_code=404, detail="Realtor not found.")
        
        # Create activity
        activity_insert = supabase_client.table("realtor_activities").insert({
            "realtor_id": realtor_id,
            "lead_id": lead_id,
            "activity_type": activity_data.get("activity_type"),
            "title": activity_data.get("title"),
            "description": activity_data.get("description"),
            "duration_minutes": activity_data.get("duration_minutes"),
            "outcome": activity_data.get("outcome")
        }).execute()
        
        return {
            "message": "Activity created successfully.",
            "activity_id": activity_insert.data[0]["id"]
        }
    except Exception as e:
        print(f"Error creating activity: {e}")
        raise HTTPException(status_code=500, detail="Could not create activity.")

@app.put("/dashboard/pipeline/{lead_id}/stage")
async def update_lead_stage(lead_id: str, stage_data: dict, request: Request):
    """Update the stage of a lead in the pipeline."""
    try:
        tenant_id = request.state.tenant_id
        new_stage = stage_data.get("stage")
        realtor_id = stage_data.get("realtor_id")
        
        # Get Supabase client
        supabase_client = create_client(settings["supabase_url"], settings["supabase_key"])
        
        # Verify realtor belongs to tenant
        realtor_query = supabase_client.table("realtors").select("id").eq("id", realtor_id).eq("tenant_id", tenant_id).execute()
        if not realtor_query.data:
            raise HTTPException(status_code=404, detail="Realtor not found.")
        
        # Update lead stage
        update_query = supabase_client.table("lead_pipeline").update({
            "stage": new_stage,
            "last_activity": "now()"
        }).eq("lead_id", lead_id).eq("realtor_id", realtor_id).execute()
        
        return {
            "message": "Lead stage updated successfully.",
            "lead_id": lead_id,
            "new_stage": new_stage
        }
    except Exception as e:
        print(f"Error updating lead stage: {e}")
        raise HTTPException(status_code=500, detail="Could not update lead stage.")

@app.post("/dashboard/email-templates")
async def create_email_template(template_data: dict, request: Request):
    """Create a new email template for a realtor."""
    try:
        tenant_id = request.state.tenant_id
        realtor_id = template_data.get("realtor_id")
        
        # Get Supabase client
        supabase_client = create_client(settings["supabase_url"], settings["supabase_key"])
        
        # Verify realtor belongs to tenant
        realtor_query = supabase_client.table("realtors").select("id").eq("id", realtor_id).eq("tenant_id", tenant_id).execute()
        if not realtor_query.data:
            raise HTTPException(status_code=404, detail="Realtor not found.")
        
        # Create email template
        template_insert = supabase_client.table("email_templates").insert({
            "realtor_id": realtor_id,
            "name": template_data.get("name"),
            "subject": template_data.get("subject"),
            "content": template_data.get("content"),
            "template_type": template_data.get("template_type", "general")
        }).execute()
        
        return {
            "message": "Email template created successfully.",
            "template_id": template_insert.data[0]["id"]
        }
    except Exception as e:
        print(f"Error creating email template: {e}")
        raise HTTPException(status_code=500, detail="Could not create email template.")

@app.get("/dashboard/email-templates/{realtor_id}")
async def get_email_templates(realtor_id: str, request: Request):
    """Get all email templates for a specific realtor."""
    try:
        tenant_id = request.state.tenant_id
        
        # Get Supabase client
        supabase_client = create_client(settings["supabase_url"], settings["supabase_key"])
        
        # Verify realtor belongs to tenant
        realtor_query = supabase_client.table("realtors").select("id").eq("id", realtor_id).eq("tenant_id", tenant_id).execute()
        if not realtor_query.data:
            raise HTTPException(status_code=404, detail="Realtor not found.")
        
        # Get email templates
        templates_query = supabase_client.table("email_templates").select("*").eq("realtor_id", realtor_id).eq("is_active", True).execute()
        
        return {
            "realtor_id": realtor_id,
            "templates": templates_query.data
        }
    except Exception as e:
        print(f"Error retrieving email templates: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve email templates.")

# =====================================================
# LIVEKIT ENDPOINTS
# =====================================================

@app.post("/livekit/generate-token")
async def generate_livekit_token(request: Request, token_data: dict):
    """Generate LiveKit access token for user."""
    try:
        # Import LiveKit dependencies
        from livekit import api
        
        # Get API key and secret from environment
        api_key = os.getenv("LIVEKIT_API_KEY", "APIk_showtimeprop_livekit")
        api_secret = os.getenv("LIVEKIT_API_SECRET", "secret_showtimeprop_livekit_key_2024")
        
        # Extract user data
        user_id = token_data.get("user_id")
        user_name = token_data.get("user_name", "Usuario")
        room_name = token_data.get("room_name", "property-agent")
        
        # Create access token
        token = api.AccessToken(api_key, api_secret)
        token.with_identity(user_id)
        token.with_name(user_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            room_list=True,
            room_create=True,
            room_record=True,
            room_admin=True,
        ))
        
        # Set expiration (1 hour)
        token.with_ttl(3600)
        
        return {
            "token": token.to_jwt(),
            "room_name": room_name,
            "expires_in": 3600
        }
        
    except Exception as e:
        print(f"Error generating LiveKit token: {e}")
        raise HTTPException(status_code=500, detail="Could not generate LiveKit token.")

@app.post("/livekit/webhook")
async def livekit_webhook(request: Request):
    """Handle LiveKit webhook events."""
    try:
        # Get the raw body
        body = await request.body()
        
        # Parse webhook data
        webhook_data = await request.json()
        
        print(f"LiveKit webhook received: {webhook_data}")
        
        # Handle different event types
        event_type = webhook_data.get("event")
        
        if event_type == "room_finished":
            # Save conversation to CRM
            room_name = webhook_data.get("room", {}).get("name")
            participants = webhook_data.get("room", {}).get("participants", [])
            
            print(f"Room finished: {room_name} with {len(participants)} participants")
            
            # Here you would save the conversation to your CRM
            # For now, just log it
            for participant in participants:
                if participant.get("identity") == "agent":
                    print(f"Agent conversation ended in room: {room_name}")
        
        elif event_type == "participant_joined":
            participant = webhook_data.get("participant", {})
            room_name = webhook_data.get("room", {}).get("name")
            print(f"Participant joined: {participant.get('identity')} in room {room_name}")
        
        elif event_type == "participant_left":
            participant = webhook_data.get("participant", {})
            room_name = webhook_data.get("room", {}).get("name")
            print(f"Participant left: {participant.get('identity')} from room {room_name}")
        
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        print(f"Error processing LiveKit webhook: {e}")
        raise HTTPException(status_code=500, detail="Could not process webhook.")

@app.get("/livekit/rooms")
async def list_livekit_rooms(request: Request):
    """List active LiveKit rooms."""
    try:
        # Import LiveKit dependencies
        from livekit import api
        
        # Get API key and secret from environment
        api_key = os.getenv("LIVEKIT_API_KEY", "APIk_showtimeprop_livekit")
        api_secret = os.getenv("LIVEKIT_API_SECRET", "secret_showtimeprop_livekit_key_2024")
        
        # Create LiveKit client
        livekit_client = api.LiveKitAPI(api_key, api_secret)
        
        # List rooms
        rooms = livekit_client.room.list_rooms()
        
        return {
            "rooms": [
                {
                    "name": room.name,
                    "num_participants": room.num_participants,
                    "creation_time": room.creation_time,
                    "turn_password": room.turn_password
                }
                for room in rooms
            ]
        }
        
    except Exception as e:
        print(f"Error listing LiveKit rooms: {e}")
        raise HTTPException(status_code=500, detail="Could not list rooms.") 