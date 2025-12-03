from fastapi import FastAPI, HTTPException, Request, Response, Query
from pydantic import BaseModel
from qdrant_client import QdrantClient, models
import os
import json
import re
from datetime import datetime
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
    
    # DEBUG: Print all relevant environment variables
    print("🔍 DEBUG - Checking environment variables:")
    print(f"  QDRANT_HOST: {os.getenv('QDRANT_HOST')}")
    print(f"  QDRANT_URL: {os.getenv('QDRANT_URL')}")
    print(f"  SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"  COLLECTION_NAME: {os.getenv('COLLECTION_NAME')}")
    
    settings = {
        "qdrant_host": os.getenv("QDRANT_HOST") or os.getenv("QDRANT_URL"),
        # Optional: allow empty if Qdrant instance doesn't require auth
        "qdrant_api_key": os.getenv("QDRANT_API_KEY", "").strip(),
        # Optional for non-AI paths
        "openai_api_key": os.getenv("OPENAI_API_KEY", "").strip(),
        "collection_name": os.getenv("COLLECTION_NAME", "propertiesV3"),
        "supabase_url": os.getenv("SUPABASE_URL"),
        "supabase_key": os.getenv("SUPABASE_KEY"),
        "supabase_db_host": os.getenv("SUPABASE_DB_HOST"),
        "supabase_db_port": os.getenv("SUPABASE_DB_PORT", "5432"),
        "supabase_db_name": os.getenv("SUPABASE_DB_NAME"),
        "supabase_db_user": os.getenv("SUPABASE_DB_USER"),
        "supabase_db_password": os.getenv("SUPABASE_DB_PASSWORD")
    }
    # Only enforce required keys - make more flexible for debugging
    required_keys = ["qdrant_host", "collection_name", "supabase_url", "supabase_key"]
    missing_keys = []
    for key in required_keys:
        if not settings.get(key):
            missing_keys.append(key.upper())
    
    # If any required keys are missing, print debug info
    if missing_keys:
        print(f"🔍 DEBUG - Missing environment variables: {missing_keys}")
        print(f"🔍 DEBUG - All settings: {settings}")
        raise RuntimeError(f"{missing_keys[0]} is not set in environment variables.")
    
    print("✅ DEBUG - All required environment variables found!")
    return settings

# Declarar variables globales que se inicializarán en @app.on_event("startup")
settings = {}
qdrant_cli = None
openai_cli = None
supabase_cli = None

app = FastAPI(
    title="Real Estate API",
    description="API to search and retrieve property data from Qdrant.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize clients when the app starts."""
    global settings, qdrant_cli, openai_cli, supabase_cli
    print("🚀 Starting FastAPI application...")
    settings = get_settings()
    
    print("🔧 Initializing Qdrant client...")
    qdrant_cli = QdrantClient(
        url=settings["qdrant_host"],
        api_key=(settings["qdrant_api_key"] or None)
    )
    
    print("🔧 Initializing OpenAI client...")
    # Asegurar que el API key no tenga espacios (doble protección)
    openai_api_key = settings["openai_api_key"].strip() if settings["openai_api_key"] else ""
    print(f"🔍 DEBUG - OpenAI API Key length: {len(openai_api_key)}, ends with space: {openai_api_key.endswith(' ') if openai_api_key else False}")
    openai_cli = OpenAI(api_key=openai_api_key)
    
    print("🔧 Initializing Supabase client...")
    supabase_cli = create_client(settings["supabase_url"], settings["supabase_key"])
    
    print(f"✅ Connecting to collection: {settings['collection_name']}")
    qdrant_cli.get_collection(collection_name=settings["collection_name"])
    
    print("✅ All clients initialized successfully!")

# --- Add CORS Middleware ---
# Define the specific origins that are allowed to make requests.
allowed_origins = [
    "http://localhost:3000",          # For local development
    "https://showtimeprop.com",       # Your main production domain
    "https://*.vercel.app",  # Permitir todos los subdominios de Vercel
    "https://properties-nuxt.vercel.app",  # URL de producción específica
    "https://www.showtimeprop.com",   # Your www production domain
    "https://bnicolini.showtimeprop.com", # Your tenant subdomains
    "https://dash.bnicolini.showtimeprop.com" # Dashboard subdomain
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
    if request_hostname.endswith('.vercel.app') or request_hostname == 'localhost':
        print(f"Request from special source '{request_hostname}'. No tenant filter will be applied.")
        tenant_id = None
    elif request_hostname == api_host:
        # For API host, set a default tenant_id for dashboard endpoints
        tenant_id = "76aa777e-fe6b-4219-b255-349e5356dcdb"  # bnicolini tenant
        print(f"Request from API host '{request_hostname}'. Using default tenant for dashboard.")
    # For production domains, extract the subdomain
    elif request_hostname.endswith(f".{prod_base_domain}"):
        # Extract subdomain part before the base domain
        temp_subdomain = request_hostname.split(f".{prod_base_domain}")[0]
        # Normalize dashboard hosts like "dash.bnicolini" -> "bnicolini"
        if temp_subdomain.startswith("dash."):
            temp_subdomain = temp_subdomain.split(".", 1)[1]
        # Avoid treating "www" or the main domain as a tenant
        if temp_subdomain and temp_subdomain != "www":
            # Shortcut: map known tenant without querying DB
            if temp_subdomain == "bnicolini":
                tenant_id = "76aa777e-fe6b-4219-b255-349e5356dcdb"
                print(f"Mapped dashboard/tenant host '{request_hostname}' to tenant '{tenant_id}' without DB lookup.")
            else:
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


# Los clientes se inicializarán en @app.on_event("startup")
# No inicializar aquí para evitar errores antes de que se carguen las variables


# --- Pydantic Models ---
class SearchRequestModel(BaseModel):
    query: str
    filters: dict = None
    top_k: int = 5

PROPERTY_TYPE_KEYWORDS = {
    "departamento": ["departamento", "departamentos", "depto", "dto"],
    "casa": ["casa", "casas", "chalet", "chalets"],
    "ph": ["ph", "propiedad horizontal"],
    "duplex": ["duplex", "dúplex"],
    "triplex": ["triplex", "tríplex"],
    "local": ["local", "locales"],
    "oficina": ["oficina", "oficinas"],
    "terreno": ["terreno", "lote", "lotes"]
}

# NEIGHBORHOODS ahora se carga dinámicamente desde Supabase
NEIGHBORHOODS_CACHE = None

def _get_neighborhoods_from_db():
    """Obtiene la lista de barrios desde la tabla neighborhoods de Supabase."""
    global NEIGHBORHOODS_CACHE
    
    if NEIGHBORHOODS_CACHE is not None:
        return NEIGHBORHOODS_CACHE
    
    try:
        if not supabase_cli:
            print("⚠️ Supabase client no inicializado, usando lista hardcodeada")
            NEIGHBORHOODS_CACHE = []
            return NEIGHBORHOODS_CACHE
        
        response = supabase_cli.table("neighborhoods").select("name, slug").execute()
        neighborhoods = []
        if response.data:
            for nb in response.data:
                neighborhoods.append(nb.get("name", "").lower())
                neighborhoods.append(nb.get("slug", "").lower())
        
        NEIGHBORHOODS_CACHE = neighborhoods
        print(f"✅ Cargados {len(neighborhoods)} barrios desde Supabase")
        return neighborhoods
    except Exception as e:
        print(f"⚠️ Error cargando barrios desde Supabase: {e}")
        NEIGHBORHOODS_CACHE = []
        return []

def _find_neighborhood_by_query(query: str):
    """Busca un barrio en la base de datos basado en la query del usuario."""
    try:
        if not supabase_cli:
            return None
        
        query_lower = query.lower()
        
        # Buscar por nombre primero
        response = supabase_cli.table("neighborhoods").select(
            "id, name, slug, bbox_min_lat, bbox_max_lat, bbox_min_lon, bbox_max_lon"
        ).ilike("name", f"%{query_lower}%").limit(1).execute()
        
        # Si no encuentra por nombre, buscar por slug
        if not response.data or len(response.data) == 0:
            response = supabase_cli.table("neighborhoods").select(
                "id, name, slug, bbox_min_lat, bbox_max_lat, bbox_min_lon, bbox_max_lon"
            ).ilike("slug", f"%{query_lower}%").limit(1).execute()
        
        if response.data and len(response.data) > 0:
            nb = response.data[0]
            return {
                "id": nb.get("id"),
                "name": nb.get("name"),
                "slug": nb.get("slug"),
                "bbox": {
                    "min_lat": nb.get("bbox_min_lat"),
                    "max_lat": nb.get("bbox_max_lat"),
                    "min_lon": nb.get("bbox_min_lon"),
                    "max_lon": nb.get("bbox_max_lon")
                }
            }
        return None
    except Exception as e:
        print(f"⚠️ Error buscando barrio en Supabase: {e}")
        import traceback
        traceback.print_exc()
        return None

def _normalise_text(value: str) -> str:
    if not value:
        return ""
    return value.lower()

def _extract_numeric(value):
    if value is None:
        return None
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None

def _parse_query_features(query: str):
    text = _normalise_text(query)
    tokens = [tok for tok in re.split(r"[^\wáéíóúñü]+", text) if tok]
    phrases = set()

    words = text.split()
    for size in (2, 3):
        for i in range(len(words) - size + 1):
            phrases.add(" ".join(words[i : i + size]))

    bedrooms = None
    ambientes = None  # Sistema argentino
    bathrooms = None
    property_types = set()
    must_have_terms = set()
    search_mode = None  # "ambientes" o "bedrooms" para saber qué sistema usa el usuario

    for canonical, variations in PROPERTY_TYPE_KEYWORDS.items():
        if any(var in text for var in variations):
            property_types.add(canonical)

    # Detectar si el usuario está usando sistema argentino ("ambientes") o internacional ("dormitorios/cuartos")
    # Priorizar "ambientes" si aparece primero en la query
    ambiente_match = re.search(r"(\d+)\s*(?:mono)?ambiente(?:s)?", text, re.IGNORECASE)
    dormitorio_match = re.search(r"(\d+)\s*(?:dormitorio|cuarto|habitaci[oó]n)(?:s|es)?", text, re.IGNORECASE)
    
    if ambiente_match:
        # Sistema argentino: "N ambientes" = living/comedor + (N-1) dormitorios
        ambientes = _extract_numeric(ambiente_match.group(1))
        search_mode = "ambientes"
        # Convertir a bedrooms para búsqueda: N ambientes = N-1 dormitorios (excepto monoambiente = 0 dormitorios)
        if ambientes == 1:
            bedrooms = 0  # Monoambiente no tiene dormitorios separados
        else:
            bedrooms = ambientes - 1  # 2 ambientes = 1 dormitorio, 3 ambientes = 2 dormitorios, etc.
    elif dormitorio_match:
        # Sistema internacional: "N dormitorios" = N dormitorios
        bedrooms = _extract_numeric(dormitorio_match.group(1))
        search_mode = "bedrooms"
        # Convertir a ambientes: N dormitorios = N+1 ambientes (0 dormitorios = 1 ambiente/monoambiente)
        ambientes = bedrooms + 1 if bedrooms is not None else None

    bathroom_match = re.search(r"(\d+)\s*(baño|baños)", text)
    if bathroom_match:
        bathrooms = _extract_numeric(bathroom_match.group(1))

    keywords_of_interest = [
        "frente al mar",
        "vista al mar",
        "vista al golf",
        "pileta",
        "piscina",
        "quincho",
        "cochera",
        "balcón",
        "balcon",
        "amueblado",
        "luminoso",
        "terraza",
        "patio",
        "jardín",
        "jardin",
    ]
    for key in keywords_of_interest:
        if key.lower() in text:
            must_have_terms.add(key.lower())

    neighborhoods = set()
    # Cargar barrios desde la base de datos
    db_neighborhoods = _get_neighborhoods_from_db()
    for neighborhood in db_neighborhoods:
        if neighborhood and neighborhood in text:
            neighborhoods.add(neighborhood)

    return {
        "tokens": tokens,
        "phrases": phrases,
        "bedrooms": bedrooms,
        "ambientes": ambientes,  # Sistema argentino
        "search_mode": search_mode,  # "ambientes" o "bedrooms"
        "bathrooms": bathrooms,
        "property_types": property_types,
        "must_have_terms": must_have_terms,
        "neighborhoods": neighborhoods,
    }

def _property_score(payload: dict, features: dict) -> int:
    score = 0
    tokens = features["tokens"]
    property_types = features["property_types"]
    neighborhoods = features["neighborhoods"]
    must_have_terms = features["must_have_terms"]

    searchable_fields = [
        _normalise_text(payload.get("title")),
        _normalise_text(payload.get("description")),
        _normalise_text(payload.get("summary")),
        _normalise_text(payload.get("address")),
        _normalise_text(payload.get("location")),
        _normalise_text(payload.get("neighborhood")),
        _normalise_text(payload.get("property_type")),
        " ".join(str(tag).lower() for tag in (payload.get("tags") or [])),
    ]

    combined_text = " ".join(field for field in searchable_fields if field)

    for token in tokens:
        if token and token in combined_text:
            score += 2

    for phrase in features["phrases"]:
        if phrase and phrase in combined_text:
            score += 4
    for neighborhood in neighborhoods:
        if neighborhood and neighborhood in combined_text:
            score += 5

    if property_types:
        prop_type_value = _normalise_text(payload.get("property_type"))
        for ptype in property_types:
            if ptype in prop_type_value:
                score += 6

    for term in must_have_terms:
        if term and term in combined_text:
            score += 5

    if features["bedrooms"] is not None:
        bedrooms_field = _extract_numeric(
            payload.get("bedrooms")
            or payload.get("ambientes")
            or payload.get("rooms")
        )
        if bedrooms_field is not None:
            if bedrooms_field == features["bedrooms"]:
                score += 6
            elif bedrooms_field > features["bedrooms"]:
                score += 3
            else:
                score -= 4

    if features["bathrooms"] is not None:
        bathrooms_field = _extract_numeric(payload.get("bathrooms"))
        if bathrooms_field is not None:
            if bathrooms_field == features["bathrooms"]:
                score += 3
            elif bathrooms_field > features["bathrooms"]:
                score += 1
            else:
                score -= 2

    return score

def _passes_filters(payload: dict, features: dict, filters: dict, neighborhood_bbox: dict = None) -> bool:
    # Manejar sistema argentino ("ambientes") vs internacional ("bedrooms")
    search_mode = features.get("search_mode")
    desired_ambientes = features.get("ambientes")
    desired_bedrooms = features.get("bedrooms")
    
    if search_mode == "ambientes" and desired_ambientes is not None:
        # Sistema argentino: buscar propiedades donde ambientes == N
        # O donde bedrooms == N-1 (excepto monoambiente)
        ambientes_raw = payload.get("ambientes")
        bedrooms_raw = payload.get("bedrooms") or payload.get("rooms")
        ambientes_field = _extract_numeric(ambientes_raw)
        bedrooms_field = _extract_numeric(bedrooms_raw)
        
        # Debug logging para entender qué valores llegan
        if desired_ambientes == 1:
            print(f"   🔍 DEBUG _passes_filters INICIO: ambientes_raw={ambientes_raw} (type={type(ambientes_raw)}), bedrooms_raw={bedrooms_raw} (type={type(bedrooms_raw)}), ambientes_field={ambientes_field}, bedrooms_field={bedrooms_field}")
        
        if ambientes_field is None and bedrooms_field is None:
            print(f"   🔍 DEBUG _passes_filters: Ambos campos son None - ambientes_raw={ambientes_raw}, bedrooms_raw={bedrooms_raw}")
            return False
        
        # Si busca monoambiente (1 ambiente)
        # UNIFICACIÓN: Aceptar propiedades con ambientes=1 O bedrooms=1 O bedrooms=0
        # IMPORTANTE: Rechazar propiedades con ambientes=2+ aunque tengan bedrooms=1
        if desired_ambientes == 1:
            # PRIMERO: Rechazar si tiene ambientes=2 o más (definitivamente NO es 1 ambiente)
            if ambientes_field is not None and ambientes_field >= 2:
                print(f"   🔍 DEBUG _passes_filters monoambiente: Rechazada por ambientes >= 2 - ambientes_field={ambientes_field}")
                return False
            
            # SEGUNDO: Aceptar si cumple alguna de estas condiciones
            match = False
            # Si tiene ambientes=1, aceptar (sin importar bedrooms)
            if ambientes_field is not None and ambientes_field == 1:
                match = True
                print(f"   ✅ DEBUG _passes_filters monoambiente: ACEPTADA por ambientes=1 - ambientes_field={ambientes_field}, bedrooms_field={bedrooms_field}")
            # Si tiene bedrooms=1 Y ambientes no es 2+, aceptar
            elif bedrooms_field is not None and bedrooms_field == 1:
                match = True
                print(f"   ✅ DEBUG _passes_filters monoambiente: ACEPTADA por bedrooms=1 - ambientes_field={ambientes_field}, bedrooms_field={bedrooms_field}")
            # Si tiene bedrooms=0, aceptar (monoambiente)
            elif bedrooms_field is not None and bedrooms_field == 0:
                match = True
                print(f"   ✅ DEBUG _passes_filters monoambiente: ACEPTADA por bedrooms=0 - ambientes_field={ambientes_field}, bedrooms_field={bedrooms_field}")
            
            if not match:
                # Log detallado para debuggear
                print(f"   🔍 DEBUG _passes_filters monoambiente: RECHAZADA - ambientes_raw={ambientes_raw}, bedrooms_raw={bedrooms_raw}, ambientes_field={ambientes_field}, bedrooms_field={bedrooms_field}, match={match}")
                return False
        else:
            # Para 2+ ambientes: ambientes == N O bedrooms == N-1
            match = False
            if ambientes_field is not None and ambientes_field == desired_ambientes:
                match = True
            elif bedrooms_field is not None and bedrooms_field == (desired_ambientes - 1):
                match = True
            if not match:
                return False
    elif search_mode == "bedrooms" and desired_bedrooms is not None:
        # Sistema internacional: buscar propiedades donde bedrooms == N
        bedrooms_field = _extract_numeric(
            payload.get("bedrooms")
            or payload.get("rooms")
        )
        if bedrooms_field is None:
            return False
        # Si busca 1 dormitorio, buscar exactamente 1. Si busca 2+, usar >=
        if desired_bedrooms == 1:
            if bedrooms_field != 1:
                return False
        else:
            if bedrooms_field < desired_bedrooms:
                return False
    elif desired_bedrooms is not None:
        # Fallback: si no hay search_mode pero hay bedrooms, usar lógica antigua
        bedrooms_field = _extract_numeric(
            payload.get("bedrooms")
            or payload.get("rooms")
        )
        if bedrooms_field is None:
            return False
        if desired_bedrooms == 1:
            if bedrooms_field != 1:
                return False
        else:
            if bedrooms_field < desired_bedrooms:
                return False

    desired_bathrooms = features.get("bathrooms")
    if desired_bathrooms is not None:
        bathrooms_field = _extract_numeric(payload.get("bathrooms"))
        if bathrooms_field is None or bathrooms_field < desired_bathrooms:
            print(f"   🔍 DEBUG _passes_filters: Rechazada por bathrooms - desired={desired_bathrooms}, actual={bathrooms_field}")
            return False

    if features.get("property_types"):
        prop_type_value = _normalise_text(payload.get("property_type") or "")
        if not any(ptype in prop_type_value for ptype in features["property_types"]):
            print(f"   🔍 DEBUG _passes_filters: Rechazada por property_types - desired={features['property_types']}, actual={prop_type_value}")
            return False

    # Verificar filtro geográfico si hay un barrio con bbox
    if neighborhood_bbox and neighborhood_bbox.get("bbox"):
        bbox = neighborhood_bbox["bbox"]
        lat = payload.get("latitude") or payload.get("lat")
        lng = payload.get("longitude") or payload.get("lng") or payload.get("lon")
        
        if lat is None or lng is None:
            # Si no hay coordenadas, verificar por texto como fallback
            location_text = _normalise_text(payload.get("location") or "") + " " + _normalise_text(
                payload.get("neighborhood") or ""
            )
            neighborhoods_in_query = features.get("neighborhoods", [])
            if not any(neigh in location_text for neigh in neighborhoods_in_query):
                print(f"   🔍 DEBUG _passes_filters: Rechazada por filtro geográfico (sin coordenadas, fallback texto) - location_text={location_text[:50]}, neighborhoods={neighborhoods_in_query}")
                return False
        else:
            # Verificar que esté dentro del bounding box
            try:
                lat = float(lat)
                lng = float(lng)
                if not (bbox["min_lat"] <= lat <= bbox["max_lat"] and 
                        bbox["min_lon"] <= lng <= bbox["max_lon"]):
                    print(f"   🔍 DEBUG _passes_filters: Rechazada por filtro geográfico (fuera de bbox) - lat={lat}, lng={lng}, bbox={bbox}")
                    return False
            except (ValueError, TypeError):
                # Si no se puede convertir, usar fallback por texto
                location_text = _normalise_text(payload.get("location") or "") + " " + _normalise_text(
                    payload.get("neighborhood") or ""
                )
                if not any(neigh in location_text for neigh in features.get("neighborhoods", [])):
                    return False
    elif features.get("neighborhoods"):
        # Si hay barrios mencionados pero no hay bbox, verificar por texto
        location_text = _normalise_text(payload.get("location") or "") + " " + _normalise_text(
            payload.get("neighborhood") or ""
        )
        neighborhoods_in_query = features["neighborhoods"]
        if not any(neigh in location_text for neigh in neighborhoods_in_query):
            print(f"   🔍 DEBUG _passes_filters: Rechazada por filtro de neighborhoods (texto) - location_text={location_text[:50]}, neighborhoods={neighborhoods_in_query}")
            return False

    if filters:
        for key, expected in filters.items():
            value = payload.get(key)
            if value is None:
                return False
            if isinstance(expected, (list, tuple, set)):
                expected_values = [str(opt).lower() for opt in expected]
                if str(value).lower() not in expected_values:
                    return False
            else:
                if str(value).lower() != str(expected).lower():
                    return False

    return True

def _fallback_semantic_search(search_request: SearchRequestModel, neighborhood_data: dict = None) -> list:
    if not qdrant_cli:
        return []

    features = _parse_query_features(search_request.query)
    limit = max(search_request.top_k * 8, 200)
    
    # Construir filtros de Qdrant para el scroll
    scroll_filter_conditions = []
    
    # Agregar filtros geográficos si hay un barrio (con margen para ser más flexible)
    if neighborhood_data and neighborhood_data.get("bbox"):
        bbox = neighborhood_data["bbox"]
        if bbox.get("min_lat") and bbox.get("max_lat") and bbox.get("min_lon") and bbox.get("max_lon"):
            # Expandir el bbox ligeramente (0.01 grados ≈ 1km) para ser más flexible
            lat_margin = (float(bbox["max_lat"]) - float(bbox["min_lat"])) * 0.1  # 10% de margen
            lon_margin = (float(bbox["max_lon"]) - float(bbox["min_lon"])) * 0.1
            scroll_filter_conditions.append(models.FieldCondition(
                key="latitude",
                range=models.Range(
                    gte=float(bbox["min_lat"]) - lat_margin,
                    lte=float(bbox["max_lat"]) + lat_margin
                )
            ))
            scroll_filter_conditions.append(models.FieldCondition(
                key="longitude",
                range=models.Range(
                    gte=float(bbox["min_lon"]) - lon_margin,
                    lte=float(bbox["max_lon"]) + lon_margin
                )
            ))
            print(f"✅ Fallback: Filtros geográficos aplicados con margen (bbox expandido ~10%)")
    
    # Agregar otros filtros estructurados
    search_mode = features.get("search_mode")
    desired_ambientes = features.get("ambientes")
    desired_bedrooms = features.get("bedrooms")
    
    if search_mode == "ambientes" and desired_ambientes is not None:
        # Sistema argentino: buscar en ambientes O bedrooms con conversión
        # Usar OR para buscar en cualquiera de los dos campos
        ambientes_conditions = []
        ambientes_conditions.append(models.FieldCondition(
            key="ambientes",
            range=models.Range(gte=desired_ambientes, lte=desired_ambientes)
        ))
        if desired_ambientes == 1:
            # UNIFICACIÓN: Monoambiente acepta bedrooms == 0 O bedrooms == 1
            ambientes_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=0, lte=1)  # Aceptar 0 o 1 dormitorio
            ))
        else:
            ambientes_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=desired_ambientes - 1, lte=desired_ambientes - 1)
            ))
        scroll_filter_conditions.append(models.Filter(should=ambientes_conditions))
    elif search_mode == "bedrooms" and desired_bedrooms is not None:
        # Sistema internacional: buscar solo en bedrooms
        if desired_bedrooms == 1:
            scroll_filter_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=1, lte=1)
            ))
        else:
            scroll_filter_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=desired_bedrooms)
            ))
    elif desired_bedrooms is not None:
        # Fallback: lógica antigua
        if desired_bedrooms == 1:
            scroll_filter_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=1, lte=1)
            ))
        else:
            scroll_filter_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=desired_bedrooms)
            ))
    
    if features.get("bathrooms") is not None:
        scroll_filter_conditions.append(models.FieldCondition(
            key="bathrooms",
            range=models.Range(gte=features["bathrooms"])
        ))
    
    if features.get("property_types"):
        property_type_values = list(features["property_types"])
        scroll_filter_conditions.append(models.FieldCondition(
            key="property_type",
            match=models.MatchAny(any=property_type_values)
        ))
    
    scroll_filter = models.Filter(must=scroll_filter_conditions) if scroll_filter_conditions else None

    try:
        scroll_results, _ = qdrant_cli.scroll(
            collection_name=settings["collection_name"],
            limit=limit,
            with_payload=True,
            with_vectors=False,
            scroll_filter=scroll_filter,
        )
        print(f"✅ Fallback scroll retornó {len(scroll_results)} resultados")
    except Exception as e:
        print(f"❌ Fallback scroll failed: {e}")
        import traceback
        traceback.print_exc()
        # Si falla con filtros, intentar sin filtros geográficos
        if neighborhood_data:
            print("🔄 Intentando fallback sin filtros geográficos...")
            try:
                # Remover filtros geográficos y mantener solo los otros
                non_geo_conditions = [c for c in scroll_filter_conditions if c.key not in ["latitude", "longitude"]]
                fallback_filter = models.Filter(must=non_geo_conditions) if non_geo_conditions else None
                scroll_results, _ = qdrant_cli.scroll(
                    collection_name=settings["collection_name"],
                    limit=limit,
                    with_payload=True,
                    with_vectors=False,
                    scroll_filter=fallback_filter,
                )
                print(f"✅ Fallback sin geográficos retornó {len(scroll_results)} resultados")
            except Exception as e2:
                print(f"❌ Fallback sin geográficos también falló: {e2}")
                return []
        else:
            return []

    scored_payloads = []
    for record in scroll_results:
        payload = record.payload
        if not _passes_filters(payload, features, search_request.filters or {}, neighborhood_data):
            continue

        score = _property_score(payload, features)
        if score > 0:
            scored_payloads.append((score, payload))

    if not scored_payloads:
        # Si no hay resultados con score > 0, incluir todos los que pasen los filtros
        for record in scroll_results:
            payload = record.payload
            if _passes_filters(payload, features, search_request.filters or {}, neighborhood_data):
                scored_payloads.append((0, payload))
    
    # Si aún no hay resultados y hay un barrio, intentar sin filtro geográfico estricto
    if not scored_payloads and neighborhood_data:
        print("⚠️ No se encontraron resultados con filtros geográficos estrictos. Intentando búsqueda más amplia...")
        try:
            # Buscar solo por tipo y características, sin filtro geográfico estricto
            relaxed_conditions = []
            search_mode = features.get("search_mode")
            desired_ambientes = features.get("ambientes")
            desired_bedrooms = features.get("bedrooms")
            
            if search_mode == "ambientes" and desired_ambientes is not None:
                # Sistema argentino: buscar en ambientes O bedrooms con conversión
                ambientes_conditions = []
                ambientes_conditions.append(models.FieldCondition(
                    key="ambientes",
                    range=models.Range(gte=desired_ambientes, lte=desired_ambientes)
                ))
                if desired_ambientes == 1:
                    # UNIFICACIÓN: Monoambiente acepta bedrooms == 0 O bedrooms == 1
                    ambientes_conditions.append(models.FieldCondition(
                        key="bedrooms",
                        range=models.Range(gte=0, lte=1)  # Aceptar 0 o 1 dormitorio
                    ))
                else:
                    ambientes_conditions.append(models.FieldCondition(
                        key="bedrooms",
                        range=models.Range(gte=desired_ambientes - 1, lte=desired_ambientes - 1)
                    ))
                relaxed_conditions.append(models.Filter(should=ambientes_conditions))
            elif search_mode == "bedrooms" and desired_bedrooms is not None:
                # Sistema internacional: buscar solo en bedrooms
                if desired_bedrooms == 1:
                    relaxed_conditions.append(models.FieldCondition(
                        key="bedrooms",
                        range=models.Range(gte=1, lte=1)
                    ))
                else:
                    relaxed_conditions.append(models.FieldCondition(
                        key="bedrooms",
                        range=models.Range(gte=desired_bedrooms)
                    ))
            elif desired_bedrooms is not None:
                # Fallback: lógica antigua
                if desired_bedrooms == 1:
                    relaxed_conditions.append(models.FieldCondition(
                        key="bedrooms",
                        range=models.Range(gte=1, lte=1)
                    ))
                else:
                    relaxed_conditions.append(models.FieldCondition(
                        key="bedrooms",
                        range=models.Range(gte=desired_bedrooms)
                    ))
            if features.get("property_types"):
                property_type_values = list(features["property_types"])
                relaxed_conditions.append(models.FieldCondition(
                    key="property_type",
                    match=models.MatchAny(any=property_type_values)
                ))
            
            relaxed_filter = models.Filter(must=relaxed_conditions) if relaxed_conditions else None
            relaxed_results, _ = qdrant_cli.scroll(
                collection_name=settings["collection_name"],
                limit=limit * 2,  # Buscar más resultados para tener más opciones
                with_payload=True,
                with_vectors=False,
                scroll_filter=relaxed_filter,
            )
            print(f"✅ Búsqueda relajada retornó {len(relaxed_results)} resultados")
            
            # Filtrar por campo neighborhood o texto del barrio
            neighborhood_names = features.get("neighborhoods", [])
            neighborhood_name_from_db = neighborhood_data.get("name", "").lower() if neighborhood_data else ""
            print(f"🔍 Buscando barrios: {neighborhood_names} (barrio DB: {neighborhood_name_from_db})")
            for record in relaxed_results:
                payload = record.payload
                # Verificar que pase filtros básicos
                passes_basic_filters = _passes_filters(payload, features, search_request.filters or {}, None)  # Sin bbox estricto
                
                if not passes_basic_filters:
                    # Log para debuggear por qué no pasa los filtros
                    ambientes_field = payload.get("ambientes")
                    bedrooms_field = payload.get("bedrooms")
                    print(f"⚠️ Propiedad rechazada por filtros: {payload.get('title', 'Sin título')[:50]} - ambientes={ambientes_field}, bedrooms={bedrooms_field}")
                    continue
                
                # Primero verificar el campo neighborhood directamente (más preciso)
                property_neighborhood = _normalise_text(payload.get("neighborhood") or "")
                neighborhood_match = False
                
                if property_neighborhood:
                    # Verificar si el neighborhood de la propiedad coincide con el barrio buscado
                    if neighborhood_name_from_db and neighborhood_name_from_db in property_neighborhood:
                        neighborhood_match = True
                    elif any(neigh.lower() in property_neighborhood for neigh in neighborhood_names):
                        neighborhood_match = True
                
                # Si no coincide por neighborhood, buscar en texto de ubicación
                if not neighborhood_match:
                    location_text = _normalise_text(payload.get("location") or "") + " " + _normalise_text(
                        payload.get("address") or ""
                    )
                    if any(neigh.lower() in location_text.lower() for neigh in neighborhood_names):
                        neighborhood_match = True
                
                if neighborhood_match:
                    score = _property_score(payload, features)
                    scored_payloads.append((score, payload))
                    print(f"✅ Propiedad encontrada por texto: {payload.get('title', 'Sin título')[:50]} - Neighborhood: {payload.get('neighborhood', 'N/A')}, ambientes={payload.get('ambientes')}, bedrooms={payload.get('bedrooms')}")
            
            print(f"✅ Búsqueda relajada encontró {len(scored_payloads)} propiedades por texto")
        except Exception as e:
            print(f"⚠️ Búsqueda relajada falló: {e}")
            import traceback
            traceback.print_exc()

    scored_payloads.sort(key=lambda item: item[0], reverse=True)
    result = [payload for _, payload in scored_payloads[: search_request.top_k]]
    print(f"✅ Fallback retornó {len(result)} propiedades después de filtrar")
    return result

# --- API Endpoints ---

@app.get("/test-tenant", summary="Test Tenant Resolution")
def test_tenant_resolution(request: Request):
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state.")
    return {"message": f"Request received successfully for tenant ID: {tenant_id}"}

@app.get("/test-update", summary="Test Container Update")
def test_update():
    return {"message": "Container updated successfully - v2.0", "timestamp": datetime.now().isoformat()}

@app.get("/test-property-endpoint", summary="Test Property Endpoint")
def test_property_endpoint():
    """Test endpoint to verify property endpoint is working."""
    return {
        "message": "Property endpoint test - v2.0",
        "timestamp": datetime.now().isoformat(),
        "endpoint_available": True
    }


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


@app.get("/properties/geojson", summary="Get Properties by Viewport (BBOX)")
def get_properties_geojson(
    request: Request,
    bbox: str = Query(..., description="Bounding box: minLon,minLat,maxLon,maxLat"),
    zoom: int = Query(12, description="Current map zoom level"),
    limit: int = Query(1000, description="Max properties to return")
):
    """
    Endpoint optimizado para cargar propiedades solo en el viewport visible.
    Retorna GeoJSON con las propiedades dentro del bounding box especificado.
    """
    tenant_id = getattr(request.state, "tenant_id", None)
    
    try:
        # Parsear bbox
        minx, miny, maxx, maxy = map(float, bbox.split(","))
        
        # Ajustar límite según zoom (menos propiedades en zooms bajos)
        if zoom < 10:
            limit = min(limit, 300)
        elif zoom < 12:
            limit = min(limit, 700)
        
        print(f"Fetching properties in BBOX: [{minx}, {miny}, {maxx}, {maxy}] at zoom {zoom} for tenant {tenant_id}")
        print(f"Collection name: {settings['collection_name']}")
        
        # Obtener propiedades de Qdrant
        results, _ = qdrant_cli.scroll(
            collection_name=settings["collection_name"],
            limit=limit,
            with_payload=True,
            with_vectors=False,
            scroll_filter=None
        )
        
        print(f"Qdrant returned {len(results)} properties")
        
        # Filtrar propiedades dentro del bbox
        features = []
        print(f"Processing {len(results)} properties from Qdrant...")
        print(f"BBOX: [{minx}, {miny}, {maxx}, {maxy}]")
        
        for record in results:
            try:
                payload = record.payload
                
                # Obtener coordenadas (soportar múltiples formatos)
                lat = payload.get('lat') or payload.get('latitude') or payload.get('latitud')
                lng = payload.get('lng') or payload.get('longitude') or payload.get('longitud') or payload.get('lon')
                
                # Si no hay coordenadas directas, intentar parsear location
                if not lat or not lng:
                    location = payload.get('location')
                    if location and isinstance(location, str) and 'POINT' in location:
                        import re
                        match = re.search(r'POINT\s*\(\s*(-?[0-9.]+)\s+(-?[0-9.]+)\s*\)', location)
                        if match:
                            lng = float(match.group(1))
                            lat = float(match.group(2))
            except Exception as e:
                print(f"Error processing property: {e}")
                continue
            
            # Convertir a float si es necesario
            try:
                lat = float(lat) if lat else None
                lng = float(lng) if lng else None
            except (ValueError, TypeError):
                continue
            
            # Debug: mostrar coordenadas de cada propiedad
            print(f"Property {payload.get('id')}: lat={lat}, lng={lng}")
            
            # Verificar que esté dentro del bbox
            if lat and lng and minx <= lng <= maxx and miny <= lat <= maxy:
                # Construir feature GeoJSON
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    },
                    "properties": {
                        **payload,
                        "images": payload.get('images', [])
                    }
                }
                features.append(feature)
        
        # Construir GeoJSON
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        print(f"Returning {len(features)} properties in viewport")
        
        # Si no hay propiedades, devolver GeoJSON vacío en lugar de error
        if len(features) == 0:
            print("No properties found in bbox, returning empty GeoJSON")
            print("DEBUG: This should return empty GeoJSON, not error")
        
        return Response(
            content=json.dumps(geojson),
            media_type="application/geo+json",
            headers={
                "Cache-Control": "public, max-age=30",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid bbox format: {str(e)}")
    except Exception as e:
        print(f"Error in geojson endpoint: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve properties.")


@app.get("/properties/{property_id}", summary="Get Property Details")
def get_property_details(property_id: str, request: Request):
    """Get detailed information for a specific property by ID."""
    try:
        # Search for the property in Qdrant - try different ID field names
        results = None
        
        # Try searching by 'id' field first
        try:
            results = qdrant_cli.scroll(
                collection_name=settings["collection_name"],
                limit=1,
                with_payload=True,
                with_vectors=False,
                scroll_filter=models.Filter(
                    must=[models.FieldCondition(key="id", match=models.MatchValue(value=property_id))]
                )
            )[0]
        except:
            pass
        
        # If not found, try searching by 'property_id' field
        if not results:
            try:
                results = qdrant_cli.scroll(
                    collection_name=settings["collection_name"],
                    limit=1,
                    with_payload=True,
                    with_vectors=False,
                    scroll_filter=models.Filter(
                        must=[models.FieldCondition(key="property_id", match=models.MatchValue(value=property_id))]
                    )
                )[0]
            except:
                pass
        
        # If still not found, try searching by 'uuid' field
        if not results:
            try:
                results = qdrant_cli.scroll(
                    collection_name=settings["collection_name"],
                    limit=1,
                    with_payload=True,
                    with_vectors=False,
                    scroll_filter=models.Filter(
                        must=[models.FieldCondition(key="uuid", match=models.MatchValue(value=property_id))]
                    )
                )[0]
            except:
                pass
        
        if not results:
            raise HTTPException(status_code=404, detail="Property not found.")
        
        property_data = results[0].payload
        
        # Generate proxy URLs for images
        images = property_data.get("images", []) or property_data.get("images_array", [])
        proxy_images = []
        for i, original_url in enumerate(images):
            proxy_url = f"https://fapi.showtimeprop.com/properties/images/{property_id}/{i}"
            proxy_images.append({
                "index": i,
                "original_url": original_url,
                "proxy_url": proxy_url
            })
        
        # Add proxy images to property data
        property_data["images"] = proxy_images
        property_data["images_array"] = proxy_images
        
        return {
            "property": property_data,
            "total_images": len(images)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting property details: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve property details.")


@app.post("/search", summary="Semantic Property Search")
def search(request: Request, search_request: SearchRequestModel):
    tenant_id = getattr(request.state, "tenant_id", None)

    print(f"🔍 Performing search for tenant: {tenant_id}")
    print(f"🔍 Query: {search_request.query}")
    print(f"🔍 Filters: {search_request.filters}")
    print(f"🔍 Top K: {search_request.top_k}")

    properties = []
    features = _parse_query_features(search_request.query)
    
    # Buscar barrio mencionado en la query
    neighborhood_data = None
    if features.get("neighborhoods"):
        # Intentar encontrar el barrio en la base de datos
        for nb_name in features["neighborhoods"]:
            neighborhood_data = _find_neighborhood_by_query(nb_name)
            if neighborhood_data:
                print(f"✅ Barrio encontrado: {neighborhood_data['name']} (bbox: {neighborhood_data['bbox']})")
                break

    # Construir filtros de Qdrant
    qdrant_conditions = []
    
    # Agregar filtros del request
    if search_request.filters:
        for field, value in search_request.filters.items():
            if isinstance(value, (list, tuple)):
                # Para valores múltiples, usar MatchAny
                qdrant_conditions.append(models.FieldCondition(
                    key=field,
                    match=models.MatchAny(any=value)
                ))
            else:
                qdrant_conditions.append(models.FieldCondition(
                    key=field,
                    match=models.MatchValue(value=value)
                ))
    
    # Agregar filtros geográficos si se encontró un barrio
    if neighborhood_data and neighborhood_data.get("bbox"):
        bbox = neighborhood_data["bbox"]
        if bbox.get("min_lat") and bbox.get("max_lat") and bbox.get("min_lon") and bbox.get("max_lon"):
            # Filtrar por latitud (bbox)
            qdrant_conditions.append(models.FieldCondition(
                key="latitude",
                range=models.Range(
                    gte=float(bbox["min_lat"]),
                    lte=float(bbox["max_lat"])
                )
            ))
            # Filtrar por longitud (bbox)
            qdrant_conditions.append(models.FieldCondition(
                key="longitude",
                range=models.Range(
                    gte=float(bbox["min_lon"]),
                    lte=float(bbox["max_lon"])
                )
            ))
            print(f"✅ Filtros geográficos aplicados: lat[{bbox['min_lat']}, {bbox['max_lat']}], lon[{bbox['min_lon']}, {bbox['max_lon']}]")
    
    # Aplicar filtros de características extraídas de la query
    search_mode = features.get("search_mode")
    desired_ambientes = features.get("ambientes")
    desired_bedrooms = features.get("bedrooms")
    
    if search_mode == "ambientes" and desired_ambientes is not None:
        # Sistema argentino: buscar en campo "ambientes" O en "bedrooms" con conversión
        # Usar OR para buscar en cualquiera de los dos campos
        ambientes_conditions = []
        
        # Condición 1: ambientes == N
        ambientes_conditions.append(models.FieldCondition(
            key="ambientes",
            range=models.Range(gte=desired_ambientes, lte=desired_ambientes)
        ))
        
        # Condición 2: bedrooms == N-1 (excepto monoambiente)
        if desired_ambientes == 1:
            # UNIFICACIÓN: Monoambiente acepta bedrooms == 0 O bedrooms == 1
            # (ambos se consideran equivalentes a 1 ambiente)
            ambientes_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=0, lte=1)  # Aceptar 0 o 1 dormitorio
            ))
        else:
            # 2+ ambientes: bedrooms == N-1
            ambientes_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=desired_ambientes - 1, lte=desired_ambientes - 1)
            ))
        
        # Usar MatchAny para buscar propiedades que cumplan cualquiera de las condiciones
        qdrant_conditions.append(models.Filter(
            should=ambientes_conditions  # OR: cumple condición 1 O condición 2
        ))
    elif search_mode == "bedrooms" and desired_bedrooms is not None:
        # Sistema internacional: buscar solo en bedrooms
        if desired_bedrooms == 1:
            qdrant_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=1, lte=1)
            ))
        else:
            qdrant_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=desired_bedrooms)
            ))
    elif desired_bedrooms is not None:
        # Fallback: lógica antigua si no hay search_mode
        if desired_bedrooms == 1:
            qdrant_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=1, lte=1)
            ))
        else:
            qdrant_conditions.append(models.FieldCondition(
                key="bedrooms",
                range=models.Range(gte=desired_bedrooms)
            ))
    
    if features.get("bathrooms") is not None:
        qdrant_conditions.append(models.FieldCondition(
            key="bathrooms",
            range=models.Range(gte=features["bathrooms"])
        ))
    
    if features.get("property_types"):
        # Buscar propiedades que coincidan con alguno de los tipos mencionados
        property_type_values = list(features["property_types"])
        qdrant_conditions.append(models.FieldCondition(
            key="property_type",
            match=models.MatchAny(any=property_type_values)
        ))

    query_filter = models.Filter(must=qdrant_conditions) if qdrant_conditions else None
    
    if query_filter:
        print(f"✅ Filtros de Qdrant aplicados: {len(qdrant_conditions)} condiciones")

    # Intentar búsqueda semántica con embeddings
    embeddings_available = bool(settings.get("openai_api_key"))
    if embeddings_available:
        try:
            print("🔍 Generando embedding con OpenAI...")
            # Logging adicional para debuggear el problema del espacio
            current_key = settings.get("openai_api_key", "")
            if current_key:
                print(f"🔍 DEBUG - API Key antes de llamada: length={len(current_key)}, ends_with_space={current_key.endswith(' ')}, repr={repr(current_key[-10:])}")
            embedding_response = openai_cli.embeddings.create(
                input=search_request.query,
                model="text-embedding-3-small"
            )
            query_vector = embedding_response.data[0].embedding
            print(f"✅ Embedding generado (dimensión: {len(query_vector)})")

            # Búsqueda en Qdrant con filtros
            search_limit = max(search_request.top_k * 3, 50)  # Buscar más resultados para filtrar después
            print(f"🔍 Buscando en Qdrant con límite: {search_limit}")
            
            hits = qdrant_cli.search(
                collection_name=settings["collection_name"],
                query_vector=query_vector,
                limit=search_limit,
                query_filter=query_filter,
                search_params=models.SearchParams(hnsw_ef=128, exact=False),
            )

            print(f"✅ Qdrant retornó {len(hits)} resultados")
            
            # Aplicar filtros adicionales de texto
            for hit in hits:
                payload = hit.payload
                # Verificar que pase los filtros de texto (keywords, frases, etc.)
                if _passes_filters(payload, features, search_request.filters or {}, neighborhood_data):
                    properties.append(payload)
                    if len(properties) >= search_request.top_k:
                        break

            print(f"✅ {len(properties)} propiedades pasaron los filtros de texto")
            
            if not properties:
                print("⚠️ Embedding search retornó resultados pero ninguno pasó los filtros estructurados.")
        except Exception as e:
            print(f"❌ Error durante búsqueda con embeddings: {e}")
            import traceback
            traceback.print_exc()
            properties = []
    else:
        print("⚠️ OPENAI_API_KEY no configurada. Usando búsqueda por keywords.")

    # Si no hay resultados, usar fallback
    if not properties:
        print("🔄 Usando búsqueda fallback por keywords...")
        properties = _fallback_semantic_search(search_request, neighborhood_data)

    if not properties:
        print("⚠️ No se encontraron propiedades")
        # Buscar alternativas: si busca 1 ambiente, buscar 2 y 3 ambientes en el mismo barrio
        alternative_properties = []
        if search_mode == "ambientes" and desired_ambientes == 1 and neighborhood_data:
            print("🔍 Buscando alternativas: propiedades con 2 o 3 ambientes en el mismo barrio...")
            for alt_ambientes in [2, 3]:
                alt_features = features.copy()
                alt_features["ambientes"] = alt_ambientes
                alt_features["bedrooms"] = alt_ambientes - 1
                alt_search_request = SearchRequestModel(
                    query=f"{search_request.query.replace('1 ambiente', f'{alt_ambientes} ambientes')}",
                    top_k=3,
                    filters=search_request.filters or {}
                )
                alt_results = _fallback_semantic_search(alt_search_request, neighborhood_data)
                if alt_results:
                    alternative_properties.extend(alt_results[:2])  # Máximo 2 por alternativa
            if alternative_properties:
                print(f"✅ Encontradas {len(alternative_properties)} propiedades alternativas (2-3 ambientes)")
                # Retornar objeto con metadata para que el agente pueda sugerir alternativas
                # El agente puede verificar si es un dict con 'alternatives' para manejar el caso
                return {
                    "properties": [],
                    "alternatives": alternative_properties,
                    "message": f"No encontré propiedades con exactamente 1 ambiente en {neighborhood_data.get('name', 'La Perla')}, pero encontré {len(alternative_properties)} propiedades con 2 o 3 ambientes en la misma zona."
                }
        # Si no hay alternativas o no aplica, retornar lista vacía normal
        return []

    print(f"✅ Retornando {len(properties[:search_request.top_k])} propiedades")
    return properties[: search_request.top_k]


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
    # Try to get tenant_id from header first, then from request state
    tenant_id = request.headers.get("X-Tenant-ID") or getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state or headers.")
    
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


@app.put("/users/{user_id}", summary="Update User Information")
def update_user(request: Request, user_id: str, user_data: dict):
    # Try to get tenant_id from header first, then from request state
    tenant_id = request.headers.get("X-Tenant-ID") or getattr(request.state, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in request state or headers.")
    
    try:
        # Verificar que el usuario pertenece al tenant
        user_check = supabase_cli.table("users").select("id").eq("id", user_id).eq("tenant_id", tenant_id).execute()
        if not user_check.data:
            raise HTTPException(status_code=404, detail="User not found or not assigned to this tenant.")
        
        # Actualizar datos del usuario
        update_data = {}
        if "full_name" in user_data:
            update_data["full_name"] = user_data["full_name"]
        if "email" in user_data:
            update_data["email"] = user_data["email"]
        if "phone" in user_data:
            update_data["phone"] = user_data["phone"]
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update.")
        
        response = supabase_cli.table("users").update(update_data).eq("id", user_id).eq("tenant_id", tenant_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found.")
        
        return {"message": "User updated successfully", "user": response.data[0]}
    except Exception as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Could not update user.")


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
# CRM ENDPOINTS FOR SHOWY CONVERSATIONS
# =====================================================

@app.post("/crm/conversations", summary="Save Conversation to CRM")
async def save_conversation_to_crm(request: Request, conversation_data: dict):
    """Save conversation data to Supabase CRM"""
    try:
        tenant_id = getattr(request.state, "tenant_id", None)
        
        # Preparar datos para Supabase
        conversation_record = {
            "realtor_id": tenant_id,
            "session_id": conversation_data.get("session_id"),
            "user_name": conversation_data.get("user_name"),
            "transcript": conversation_data.get("transcript", ""),
            "summary": conversation_data.get("summary", ""),
            "property_preferences": conversation_data.get("property_preferences", {}),
            "lead_score": conversation_data.get("lead_score", 0),
            "language": conversation_data.get("language", "es"),
            "status": conversation_data.get("status", "completed")
        }
        
        # Insertar en Supabase
        result = supabase_cli.table("conversations").insert(conversation_record).execute()
        
        if result.data:
            conversation_id = result.data[0]["id"]
            
            # Si hay información de contacto, crear lead
            if conversation_data.get("contact_info"):
                lead_record = {
                    "conversation_id": conversation_id,
                    "realtor_id": tenant_id,
                    "contact_info": conversation_data.get("contact_info"),
                    "property_preferences": conversation_data.get("property_preferences", {}),
                    "urgency": conversation_data.get("urgency"),
                    "purpose": conversation_data.get("purpose"),
                    "transaction_type": conversation_data.get("transaction_type"),
                    "condition_preference": conversation_data.get("condition_preference"),
                    "lead_score": conversation_data.get("lead_score", 0),
                    "status": "new",
                    "next_action": conversation_data.get("next_action", "Contactar cliente")
                }
                
                lead_result = supabase_cli.table("leads").insert(lead_record).execute()
                
                return {
                    "conversation_id": conversation_id,
                    "lead_id": lead_result.data[0]["id"] if lead_result.data else None,
                    "message": "Conversación y lead guardados exitosamente"
                }
            
            return {
                "conversation_id": conversation_id,
                "message": "Conversación guardada exitosamente"
            }
        else:
            raise HTTPException(status_code=500, detail="Error guardando conversación")
            
    except Exception as e:
        print(f"Error guardando conversación: {e}")
        raise HTTPException(status_code=500, detail="Could not save conversation to CRM")

@app.post("/crm/leads", summary="Create Lead from Conversation")
async def create_lead_from_conversation(request: Request, lead_data: dict):
    """Create a lead from conversation data"""
    try:
        tenant_id = getattr(request.state, "tenant_id", None)
        
        lead_record = {
            "conversation_id": lead_data.get("conversation_id"),
            "realtor_id": tenant_id,
            "contact_info": lead_data.get("contact_info"),
            "property_preferences": lead_data.get("property_preferences", {}),
            "urgency": lead_data.get("urgency"),
            "purpose": lead_data.get("purpose"),
            "transaction_type": lead_data.get("transaction_type"),
            "condition_preference": lead_data.get("condition_preference"),
            "lead_score": lead_data.get("lead_score", 0),
            "status": "new",
            "next_action": lead_data.get("next_action", "Contactar cliente")
        }
        
        result = supabase_cli.table("leads").insert(lead_record).execute()
        
        if result.data:
            return {
                "lead_id": result.data[0]["id"],
                "message": "Lead creado exitosamente"
            }
        else:
            raise HTTPException(status_code=500, detail="Error creando lead")
            
    except Exception as e:
        print(f"Error creando lead: {e}")
        raise HTTPException(status_code=500, detail="Could not create lead")

@app.get("/crm/conversations/{tenant_id}", summary="Get Conversations for Tenant")
async def get_conversations_for_tenant(tenant_id: str, request: Request):
    """Get all conversations for a specific tenant"""
    try:
        # Verificar que el tenant_id coincida con el del request
        request_tenant_id = getattr(request.state, "tenant_id", None)
        if request_tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = supabase_cli.table("conversations").select("*").eq("realtor_id", tenant_id).order("created_at", desc=True).execute()
        
        return {
            "conversations": result.data,
            "total": len(result.data)
        }
        
    except Exception as e:
        print(f"Error obteniendo conversaciones: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve conversations")

@app.get("/crm/leads/{tenant_id}", summary="Get Leads for Tenant")
async def get_leads_for_tenant(tenant_id: str, request: Request):
    """Get all leads for a specific tenant"""
    try:
        # Verificar que el tenant_id coincida con el del request
        request_tenant_id = getattr(request.state, "tenant_id", None)
        if request_tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = supabase_cli.table("leads").select("*").eq("realtor_id", tenant_id).order("created_at", desc=True).execute()
        
        return {
            "leads": result.data,
            "total": len(result.data)
        }
        
    except Exception as e:
        print(f"Error obteniendo leads: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve leads")

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

# =====================================================
# IMAGE PROXY ENDPOINTS
# =====================================================

@app.get("/properties/images/{property_id}/{image_index}")
async def serve_property_image(property_id: str, image_index: int, request: Request):
    """Proxy endpoint to serve property images from external sources."""
    try:
        import httpx
        from urllib.parse import urlencode
        
        # Get Supabase client
        supabase_client = create_client(settings["supabase_url"], settings["supabase_key"])
        
        # Get property data to find the original image URL
        # First, let's try to get the property from Qdrant
        try:
            # Search for the property in Qdrant - try different ID field names
            results = None
            
            # Try searching by 'id' field first
            try:
                results = qdrant_cli.scroll(
                    collection_name=settings["collection_name"],
                    limit=1,
                    with_payload=True,
                    with_vectors=False,
                    scroll_filter=models.Filter(
                        must=[models.FieldCondition(key="id", match=models.MatchValue(value=property_id))]
                    )
                )[0]
            except:
                pass
            
            # If not found, try searching by 'property_id' field
            if not results:
                try:
                    results = qdrant_cli.scroll(
                        collection_name=settings["collection_name"],
                        limit=1,
                        with_payload=True,
                        with_vectors=False,
                        scroll_filter=models.Filter(
                            must=[models.FieldCondition(key="property_id", match=models.MatchValue(value=property_id))]
                        )
                    )[0]
                except:
                    pass
            
            # If still not found, try searching by 'uuid' field
            if not results:
                try:
                    results = qdrant_cli.scroll(
                        collection_name=settings["collection_name"],
                        limit=1,
                        with_payload=True,
                        with_vectors=False,
                        scroll_filter=models.Filter(
                            must=[models.FieldCondition(key="uuid", match=models.MatchValue(value=property_id))]
                        )
                    )[0]
                except:
                    pass
            
            if not results:
                raise HTTPException(status_code=404, detail="Property not found.")
            
            property_data = results[0].payload
            images = property_data.get("images", []) or property_data.get("images_array", [])
            
            if not images or image_index >= len(images):
                raise HTTPException(status_code=404, detail="Image not found.")
            
            image_url = images[image_index]
            
        except Exception as e:
            print(f"Error getting property from Qdrant: {e}")
            raise HTTPException(status_code=404, detail="Property not found.")
        
        # Download the image from the external source
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(image_url, timeout=30.0)
                response.raise_for_status()
                
                # Get content type
                content_type = response.headers.get("content-type", "image/jpeg")
                
                # Return the image with proper headers
                return Response(
                    content=response.content,
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET",
                        "Access-Control-Allow-Headers": "*",
                    }
                )
                
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Image request timeout.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    raise HTTPException(status_code=403, detail="External server blocked access to image.")
                elif e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail="Image not found on external server.")
                else:
                    raise HTTPException(status_code=502, detail=f"External server error: {e.response.status_code}")
            except Exception as e:
                print(f"Error downloading image: {e}")
                raise HTTPException(status_code=500, detail="Could not download image.")
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in image proxy: {e}")
        raise HTTPException(status_code=500, detail="Could not serve image.")

@app.get("/properties/images/{property_id}/all")
async def get_property_images_urls(property_id: str, request: Request):
    """Get all image URLs for a property with proxy endpoints."""
    try:
        # Search for the property in Qdrant - try different ID field names
        results = None
        
        # Try searching by 'id' field first
        try:
            results = qdrant_cli.scroll(
                collection_name=settings["collection_name"],
                limit=1,
                with_payload=True,
                with_vectors=False,
                scroll_filter=models.Filter(
                    must=[models.FieldCondition(key="id", match=models.MatchValue(value=property_id))]
                )
            )[0]
        except:
            pass
        
        # If not found, try searching by 'property_id' field
        if not results:
            try:
                results = qdrant_cli.scroll(
                    collection_name=settings["collection_name"],
                    limit=1,
                    with_payload=True,
                    with_vectors=False,
                    scroll_filter=models.Filter(
                        must=[models.FieldCondition(key="property_id", match=models.MatchValue(value=property_id))]
                    )
                )[0]
            except:
                pass
        
        # If still not found, try searching by 'uuid' field
        if not results:
            try:
                results = qdrant_cli.scroll(
                    collection_name=settings["collection_name"],
                    limit=1,
                    with_payload=True,
                    with_vectors=False,
                    scroll_filter=models.Filter(
                        must=[models.FieldCondition(key="uuid", match=models.MatchValue(value=property_id))]
                    )
                )[0]
            except:
                pass
        
        if not results:
            raise HTTPException(status_code=404, detail="Property not found.")
        
        property_data = results[0].payload
        images = property_data.get("images", []) or property_data.get("images_array", [])
        
        # Generate proxy URLs for all images
        proxy_urls = []
        for i, original_url in enumerate(images):
            proxy_url = f"https://fapi.showtimeprop.com/properties/images/{property_id}/{i}"
            proxy_urls.append({
                "index": i,
                "original_url": original_url,
                "proxy_url": proxy_url
            })
        
        return {
            "property_id": property_id,
            "images": proxy_urls,
            "total_images": len(images)
        }
        
    except Exception as e:
        print(f"Error getting property images: {e}")
        raise HTTPException(status_code=500, detail="Could not get property images.")

@app.get("/proxy/health")
async def check_proxy_health():
    """Endpoint para verificar la salud del proxy."""
    try:
        # Hacer una petición de prueba a una imagen conocida
        test_url = "https://via.placeholder.com/150x150.jpg"
        async with httpx.AsyncClient() as client:
            response = await client.head(test_url, timeout=10.0)

            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/debug/image-formats")
async def check_image_formats():
    """Endpoint temporal para verificar formatos de imagen en la base de datos."""
    try:
        # Obtener algunas propiedades de ejemplo
        results = qdrant_cli.scroll(
            collection_name=settings["collection_name"],
            limit=50,  # Solo las primeras 50 para no sobrecargar
            with_payload=True,
            with_vectors=False,
        )[0]

        image_formats = {
            "jpg": 0,
            "jpeg": 0,
            "png": 0,
            "avif": 0,
            "webp": 0,
            "other": 0
        }
        
        total_images = 0
        properties_with_images = 0
        sample_urls = []
        problematic_urls = []

        for result in results:
            property_data = result.payload
            images = property_data.get("images", []) or property_data.get("images_array", [])
            
            if images and len(images) > 0:
                properties_with_images += 1
                
                for image_url in images:
                    total_images += 1
                    
                    # Guardar algunas URLs de ejemplo
                    if len(sample_urls) < 10:
                        sample_urls.append(image_url)
                    
                    # Analizar extensión
                    extension = image_url.split('.')[-1].lower() if '.' in image_url else 'unknown'
                    
                    if 'jpg' in extension:
                        image_formats["jpg"] += 1
                        # Verificar si es una URL problemática (.jpg pero no .avif)
                        if not extension.endswith('avif'):
                            problematic_urls.append(image_url)
                    elif 'jpeg' in extension:
                        image_formats["jpeg"] += 1
                    elif 'png' in extension:
                        image_formats["png"] += 1
                    elif 'avif' in extension:
                        image_formats["avif"] += 1
                    elif 'webp' in extension:
                        image_formats["webp"] += 1
                    else:
                        image_formats["other"] += 1

        return {
            "total_properties_checked": len(results),
            "properties_with_images": properties_with_images,
            "total_images": total_images,
            "formats": image_formats,
            "sample_urls": sample_urls[:5],  # Primeras 5 URLs de ejemplo
            "problematic_urls": problematic_urls[:10],  # Primeras 10 URLs problemáticas
            "timestamp": datetime.now().isoformat()
        }
#==
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
