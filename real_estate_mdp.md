--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4 (Debian 16.4-1.pgdg110+2)
-- Dumped by pg_dump version 16.9

-- Started on 2025-06-15 22:41:34 UTC

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 15 (class 2615 OID 19300)
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger;


ALTER SCHEMA tiger OWNER TO postgres;

--
-- TOC entry 16 (class 2615 OID 19556)
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger_data;


ALTER SCHEMA tiger_data OWNER TO postgres;

--
-- TOC entry 14 (class 2615 OID 19121)
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- TOC entry 5239 (class 0 OID 0)
-- Dependencies: 14
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- TOC entry 8 (class 3079 OID 19820)
-- Name: btree_gin; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS btree_gin WITH SCHEMA public;


--
-- TOC entry 5240 (class 0 OID 0)
-- Dependencies: 8
-- Name: EXTENSION btree_gin; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION btree_gin IS 'support for indexing common datatypes in GIN';


--
-- TOC entry 4 (class 3079 OID 19288)
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- TOC entry 5241 (class 0 OID 0)
-- Dependencies: 4
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- TOC entry 9 (class 3079 OID 20256)
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- TOC entry 5242 (class 0 OID 0)
-- Dependencies: 9
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- TOC entry 7 (class 3079 OID 19739)
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- TOC entry 5243 (class 0 OID 0)
-- Dependencies: 7
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- TOC entry 2 (class 3079 OID 18043)
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- TOC entry 5244 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- TOC entry 5 (class 3079 OID 19301)
-- Name: postgis_tiger_geocoder; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder WITH SCHEMA tiger;


--
-- TOC entry 5245 (class 0 OID 0)
-- Dependencies: 5
-- Name: EXTENSION postgis_tiger_geocoder; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_tiger_geocoder IS 'PostGIS tiger geocoder and reverse geocoder';


--
-- TOC entry 3 (class 3079 OID 19122)
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- TOC entry 5246 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


--
-- TOC entry 6 (class 3079 OID 19728)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5247 (class 0 OID 0)
-- Dependencies: 6
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 617 (class 1255 OID 20575)
-- Name: calculate_days_on_market(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calculate_days_on_market() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Intentar parsear la fecha custom o usar fecha actual
    BEGIN
        NEW.days_on_market = EXTRACT(DAY FROM NOW() - 
            TO_TIMESTAMP(NEW.first_scraped_at, 'DD Mon YYYY - HH24:MI')
        );
    EXCEPTION WHEN OTHERS THEN
        NEW.days_on_market = 0;
    END;
    
    -- CAMBIO CRÍTICO: usar last_updated_at en lugar de updated_at
    NEW.last_updated_at = NOW();
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.calculate_days_on_market() OWNER TO postgres;

--
-- TOC entry 729 (class 1255 OID 20594)
-- Name: find_properties_near_point(numeric, numeric, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.find_properties_near_point(search_lat numeric, search_lng numeric, radius_meters integer DEFAULT 1000, max_results integer DEFAULT 50) RETURNS TABLE(property_id uuid, title text, address text, distance_meters integer, price_display numeric)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.title,
        p.address,
        ST_Distance(
            p.location,
            ST_SetSRID(ST_MakePoint(search_lng, search_lat), 4326)::geography
        )::INTEGER as distance_meters,
        CASE 
            WHEN p.price IS NOT NULL THEN p.price::DECIMAL / 100 
            ELSE NULL 
        END as price_display
    FROM properties p
    WHERE p.is_active = true
      AND p.location IS NOT NULL
      AND ST_DWithin(
          p.location::geography,
          ST_SetSRID(ST_MakePoint(search_lng, search_lat), 4326)::geography,
          radius_meters
      )
    ORDER BY p.location <-> ST_SetSRID(ST_MakePoint(search_lng, search_lat), 4326)
    LIMIT max_results;
END;
$$;


ALTER FUNCTION public.find_properties_near_point(search_lat numeric, search_lng numeric, radius_meters integer, max_results integer) OWNER TO postgres;

--
-- TOC entry 608 (class 1255 OID 20595)
-- Name: get_agent_dashboard_stats(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_agent_dashboard_stats(agent_uuid uuid) RETURNS json
    LANGUAGE plpgsql
    AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_properties', COALESCE(COUNT(DISTINCT p.id), 0),
        'total_clients', COALESCE(COUNT(DISTINCT c.id), 0),
        'total_favorites', COALESCE(COUNT(DISTINCT cf.id), 0),
        'total_views', COALESCE(SUM(p.views_count), 0),
        'properties_by_status', (
            SELECT json_object_agg(estado, count)
            FROM (
                SELECT p2.estado, COUNT(*) as count
                FROM properties p2
                WHERE p2.managed_by_agent_id = agent_uuid
                GROUP BY p2.estado
            ) status_counts
        ),
        'recent_activity', (
            SELECT json_agg(
                json_build_object(
                    'type', 'property_view',
                    'property_title', p3.title,
                    'client_name', c2.name,
                    'viewed_at', pv.viewed_at
                )
            )
            FROM property_views pv
            LEFT JOIN properties p3 ON pv.property_id = p3.id
            LEFT JOIN clients c2 ON pv.client_id = c2.id
            WHERE pv.agent_id = agent_uuid
            ORDER BY pv.viewed_at DESC
            LIMIT 10
        )
    ) INTO result
    FROM properties p
    LEFT JOIN clients c ON c.agent_id = agent_uuid
    LEFT JOIN client_favorites cf ON cf.client_id = c.id
    WHERE p.managed_by_agent_id = agent_uuid OR p.managed_by_agent_id IS NULL;
    
    RETURN result;
END;
$$;


ALTER FUNCTION public.get_agent_dashboard_stats(agent_uuid uuid) OWNER TO postgres;

--
-- TOC entry 1228 (class 1255 OID 20577)
-- Name: update_property_counters(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_property_counters() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Actualizar contador de favoritos
    UPDATE properties 
    SET favorites_count = (
        SELECT COUNT(*) FROM client_favorites 
        WHERE property_id = COALESCE(NEW.property_id, OLD.property_id)
    )
    WHERE id = COALESCE(NEW.property_id, OLD.property_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$;


ALTER FUNCTION public.update_property_counters() OWNER TO postgres;

--
-- TOC entry 476 (class 1255 OID 20571)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.last_updated_at = NOW();  -- Cambio crítico: usar last_updated_at
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 291 (class 1259 OID 20288)
-- Name: data_sources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_sources (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    base_url text NOT NULL,
    scraper_config jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    last_scraped_at timestamp with time zone,
    total_properties_scraped integer DEFAULT 0
);


ALTER TABLE public.data_sources OWNER TO postgres;

--
-- TOC entry 293 (class 1259 OID 20319)
-- Name: properties; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.properties (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    scraped_id character varying(100) NOT NULL,
    scraped_url text NOT NULL,
    detail_url text,
    hash_content character varying(255) NOT NULL,
    data_source_id integer,
    title text NOT NULL,
    description text,
    address text,
    barrio character varying(255),
    localidad character varying(255) DEFAULT 'Mar del Plata'::character varying,
    property_type character varying(100),
    tipo_operacion character varying(50) NOT NULL,
    estado character varying(50) DEFAULT 'DISPONIBLE'::character varying,
    luminosidad text,
    vista_principal character varying(100),
    distancia_almar text,
    info_entornocomercial text,
    tour_virtual text,
    area_m2 integer,
    bedrooms integer,
    bathrooms integer,
    ambientes integer,
    amenities jsonb,
    price bigint,
    price_currency character varying(10) DEFAULT 'USD'::character varying,
    price_per_m2 numeric(10,2),
    location public.geometry(Point,4326),
    image_url text,
    images_array jsonb,
    logo_inmobiliaria_url text,
    inmobiliaria character varying(255),
    inmobiliaria_email character varying(255),
    inmobiliaria_phone character varying(50),
    inmobiliaria_whatsapp character varying(50),
    inmobiliaria_facebook text,
    inmobiliaria_instagram text,
    status character varying(50) DEFAULT 'active'::character varying,
    views_count integer DEFAULT 0,
    leads_count integer DEFAULT 0,
    favorites_count integer DEFAULT 0,
    days_on_market integer DEFAULT 0,
    market_value_estimate bigint,
    managed_by_agent_id uuid,
    visibility_level character varying(50) DEFAULT 'public'::character varying,
    is_active boolean DEFAULT true,
    first_scraped_at text NOT NULL,
    last_scraped_at text NOT NULL,
    last_updated_at timestamp with time zone DEFAULT now(),
    inmobiliarias_array jsonb DEFAULT '[]'::jsonb,
    property_unique_hash character varying(255),
    latitude numeric(10,8),
    longitude numeric(11,8),
    CONSTRAINT valid_area CHECK (((area_m2 IS NULL) OR (area_m2 > 0))),
    CONSTRAINT valid_coordinates CHECK (((location IS NULL) OR (((public.st_x(location) >= ('-180'::integer)::double precision) AND (public.st_x(location) <= (180)::double precision)) AND ((public.st_y(location) >= ('-90'::integer)::double precision) AND (public.st_y(location) <= (90)::double precision))))),
    CONSTRAINT valid_location CHECK (public.st_isvalid(location)),
    CONSTRAINT valid_price CHECK (((price IS NULL) OR (price >= 0))),
    CONSTRAINT valid_rooms CHECK ((((bedrooms IS NULL) OR (bedrooms >= 0)) AND ((bathrooms IS NULL) OR (bathrooms >= 0)) AND ((ambientes IS NULL) OR (ambientes >= 0))))
);


ALTER TABLE public.properties OWNER TO postgres;

--
-- TOC entry 303 (class 1259 OID 20579)
-- Name: active_properties_with_location; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_properties_with_location AS
 SELECT p.id,
    p.scraped_id,
    p.title,
    p.address,
    p.barrio,
    p.localidad,
    p.property_type,
    p.tipo_operacion,
    p.estado,
    p.price,
    p.price_currency,
        CASE
            WHEN (p.price IS NOT NULL) THEN ((p.price)::numeric / (100)::numeric)
            ELSE NULL::numeric
        END AS price_display,
    p.area_m2,
    p.bedrooms,
    p.bathrooms,
    p.ambientes,
    public.st_x(p.location) AS longitude,
    public.st_y(p.location) AS latitude,
    p.days_on_market,
    p.views_count,
    p.leads_count,
    p.favorites_count,
    p.image_url,
    p.inmobiliaria,
    p.last_scraped_at,
    ds.name AS source_name
   FROM (public.properties p
     LEFT JOIN public.data_sources ds ON ((p.data_source_id = ds.id)))
  WHERE ((p.is_active = true) AND ((p.status)::text = 'active'::text) AND (p.location IS NOT NULL));


ALTER VIEW public.active_properties_with_location OWNER TO postgres;

--
-- TOC entry 292 (class 1259 OID 20301)
-- Name: agents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agents (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    email character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    phone character varying(50),
    company_name character varying(255),
    logo_url text,
    subscription_tier character varying(50) DEFAULT 'basic'::character varying,
    max_properties integer DEFAULT 100,
    max_clients integer DEFAULT 50,
    white_label_domain character varying(255),
    custom_colors jsonb,
    custom_branding jsonb,
    is_active boolean DEFAULT true,
    last_login_at timestamp with time zone,
    properties_count integer DEFAULT 0,
    clients_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.agents OWNER TO postgres;

--
-- TOC entry 304 (class 1259 OID 20584)
-- Name: barrio_analytics; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.barrio_analytics AS
 SELECT barrio,
    count(*) AS total_properties,
    count(*) FILTER (WHERE ((tipo_operacion)::text = 'VENTA'::text)) AS properties_for_sale,
    count(*) FILTER (WHERE ((tipo_operacion)::text = 'ALQUILER'::text)) AS properties_for_rent,
    avg(((price)::numeric / (100)::numeric)) AS avg_price,
    percentile_cont((0.5)::double precision) WITHIN GROUP (ORDER BY ((((price)::numeric / (100)::numeric))::double precision)) AS median_price,
    avg(price_per_m2) AS avg_price_per_m2,
    avg(area_m2) AS avg_area,
    avg(days_on_market) AS avg_days_on_market,
    avg(views_count) AS avg_views,
    sum(favorites_count) AS total_favorites
   FROM public.properties p
  WHERE ((is_active = true) AND (barrio IS NOT NULL) AND (price IS NOT NULL))
  GROUP BY barrio
  ORDER BY (count(*)) DESC;


ALTER VIEW public.barrio_analytics OWNER TO postgres;

--
-- TOC entry 296 (class 1259 OID 20390)
-- Name: client_favorites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_favorites (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid,
    property_id uuid,
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.client_favorites OWNER TO postgres;

--
-- TOC entry 298 (class 1259 OID 20437)
-- Name: client_searches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_searches (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid,
    search_query text,
    filters_used jsonb,
    results_count integer,
    search_polygon public.geometry(Polygon,4326),
    properties_clicked uuid[],
    properties_favorited uuid[],
    searched_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.client_searches OWNER TO postgres;

--
-- TOC entry 295 (class 1259 OID 20369)
-- Name: clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clients (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    agent_id uuid,
    email character varying(255),
    name character varying(255) NOT NULL,
    phone character varying(50),
    min_price bigint,
    max_price bigint,
    preferred_areas text[],
    property_types text[],
    operation_types text[],
    min_bedrooms integer,
    max_bedrooms integer,
    min_area_m2 integer,
    max_area_m2 integer,
    search_polygon public.geometry(Polygon,4326),
    lead_score integer DEFAULT 0,
    lead_source character varying(100),
    status character varying(50) DEFAULT 'new'::character varying,
    priority character varying(20) DEFAULT 'medium'::character varying,
    notes text,
    tags text[],
    last_contact_at timestamp with time zone,
    last_property_viewed_at timestamp with time zone,
    last_search_at timestamp with time zone,
    total_property_views integer DEFAULT 0,
    total_favorites integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT belongs_to_agent CHECK ((agent_id IS NOT NULL))
);


ALTER TABLE public.clients OWNER TO postgres;

--
-- TOC entry 302 (class 1259 OID 20522)
-- Name: daily_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.daily_stats (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    stat_date date NOT NULL,
    properties_scraped integer DEFAULT 0,
    new_properties integer DEFAULT 0,
    updated_properties integer DEFAULT 0,
    scraping_errors integer DEFAULT 0,
    total_views integer DEFAULT 0,
    unique_visitors integer DEFAULT 0,
    new_clients integer DEFAULT 0,
    new_favorites integer DEFAULT 0,
    searches_performed integer DEFAULT 0,
    active_agents integer DEFAULT 0,
    properties_shared integer DEFAULT 0,
    client_interactions integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.daily_stats OWNER TO postgres;

--
-- TOC entry 290 (class 1259 OID 20287)
-- Name: data_sources_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_sources_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.data_sources_id_seq OWNER TO postgres;

--
-- TOC entry 5248 (class 0 OID 0)
-- Dependencies: 290
-- Name: data_sources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_sources_id_seq OWNED BY public.data_sources.id;


--
-- TOC entry 301 (class 1259 OID 20505)
-- Name: market_analytics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_analytics (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    area_name character varying(255) NOT NULL,
    analysis_date date NOT NULL,
    analysis_period character varying(20) DEFAULT 'monthly'::character varying,
    avg_price_per_m2 numeric(10,2),
    median_price bigint,
    min_price bigint,
    max_price bigint,
    total_properties integer DEFAULT 0,
    properties_for_sale integer DEFAULT 0,
    properties_for_rent integer DEFAULT 0,
    properties_sold integer DEFAULT 0,
    avg_days_on_market integer,
    departamentos_count integer DEFAULT 0,
    casas_count integer DEFAULT 0,
    ph_count integer DEFAULT 0,
    avg_area_m2 numeric(8,2),
    price_change_30d numeric(5,2),
    price_change_90d numeric(5,2),
    inventory_change_30d numeric(5,2),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.market_analytics OWNER TO postgres;

--
-- TOC entry 294 (class 1259 OID 20355)
-- Name: price_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.price_history (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    property_id uuid,
    old_price bigint,
    new_price bigint,
    price_currency character varying(10),
    change_percentage numeric(5,2),
    change_reason character varying(100),
    detected_at timestamp with time zone DEFAULT now(),
    scraper_source text,
    notes text
);


ALTER TABLE public.price_history OWNER TO postgres;

--
-- TOC entry 297 (class 1259 OID 20411)
-- Name: property_views; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.property_views (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    property_id uuid,
    client_id uuid,
    agent_id uuid,
    ip_address inet,
    user_agent text,
    referrer text,
    session_id character varying(255),
    time_spent_seconds integer,
    images_viewed integer DEFAULT 0,
    contact_info_viewed boolean DEFAULT false,
    viewed_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.property_views OWNER TO postgres;

--
-- TOC entry 300 (class 1259 OID 20477)
-- Name: saved_map_searches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saved_map_searches (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid,
    agent_id uuid,
    name character varying(255) NOT NULL,
    description text,
    search_polygon public.geometry(Polygon,4326),
    min_price bigint,
    max_price bigint,
    property_types text[],
    operation_types text[],
    min_bedrooms integer,
    max_bedrooms integer,
    min_area_m2 integer,
    max_area_m2 integer,
    required_amenities text[],
    excluded_amenities text[],
    notify_new_properties boolean DEFAULT true,
    notify_price_changes boolean DEFAULT false,
    notify_status_changes boolean DEFAULT true,
    notification_frequency character varying(50) DEFAULT 'immediate'::character varying,
    notification_methods text[] DEFAULT ARRAY['email'::text],
    last_notification_sent timestamp with time zone,
    total_notifications_sent integer DEFAULT 0,
    matching_properties_count integer DEFAULT 0,
    last_check_at timestamp with time zone,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.saved_map_searches OWNER TO postgres;

--
-- TOC entry 299 (class 1259 OID 20451)
-- Name: shared_properties; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shared_properties (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    property_id uuid,
    agent_id uuid,
    custom_title text,
    custom_description text,
    custom_contact_info jsonb,
    hide_original_agent boolean DEFAULT false,
    custom_branding jsonb,
    share_token character varying(255) NOT NULL,
    is_password_protected boolean DEFAULT false,
    share_password character varying(255),
    expires_at timestamp with time zone,
    max_views integer,
    views_count integer DEFAULT 0,
    unique_visitors integer DEFAULT 0,
    last_viewed_at timestamp with time zone,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.shared_properties OWNER TO postgres;

--
-- TOC entry 305 (class 1259 OID 20589)
-- Name: top_agents_metrics; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.top_agents_metrics AS
 SELECT a.id,
    a.name,
    a.company_name,
    a.email,
    count(DISTINCT p.id) AS total_properties,
    count(DISTINCT c.id) AS total_clients,
    count(DISTINCT cf.id) AS total_favorites_received,
    avg(p.views_count) AS avg_property_views,
    sum(pv.time_spent_seconds) AS total_engagement_time,
    a.subscription_tier,
    a.created_at
   FROM ((((public.agents a
     LEFT JOIN public.properties p ON ((p.managed_by_agent_id = a.id)))
     LEFT JOIN public.clients c ON ((c.agent_id = a.id)))
     LEFT JOIN public.client_favorites cf ON ((cf.client_id = c.id)))
     LEFT JOIN public.property_views pv ON ((pv.agent_id = a.id)))
  WHERE (a.is_active = true)
  GROUP BY a.id, a.name, a.company_name, a.email, a.subscription_tier, a.created_at
  ORDER BY (count(DISTINCT p.id)) DESC, (count(DISTINCT c.id)) DESC;


ALTER VIEW public.top_agents_metrics OWNER TO postgres;

--
-- TOC entry 4774 (class 2604 OID 20291)
-- Name: data_sources id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_sources ALTER COLUMN id SET DEFAULT nextval('public.data_sources_id_seq'::regclass);


--
-- TOC entry 4980 (class 2606 OID 20318)
-- Name: agents agents_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_email_key UNIQUE (email);


--
-- TOC entry 4982 (class 2606 OID 20316)
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- TOC entry 5013 (class 2606 OID 20400)
-- Name: client_favorites client_favorites_client_id_property_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_favorites
    ADD CONSTRAINT client_favorites_client_id_property_id_key UNIQUE (client_id, property_id);


--
-- TOC entry 5015 (class 2606 OID 20398)
-- Name: client_favorites client_favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_favorites
    ADD CONSTRAINT client_favorites_pkey PRIMARY KEY (id);


--
-- TOC entry 5022 (class 2606 OID 20445)
-- Name: client_searches client_searches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_searches
    ADD CONSTRAINT client_searches_pkey PRIMARY KEY (id);


--
-- TOC entry 5009 (class 2606 OID 20384)
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- TOC entry 5038 (class 2606 OID 20540)
-- Name: daily_stats daily_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_stats
    ADD CONSTRAINT daily_stats_pkey PRIMARY KEY (id);


--
-- TOC entry 5040 (class 2606 OID 20542)
-- Name: daily_stats daily_stats_stat_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_stats
    ADD CONSTRAINT daily_stats_stat_date_key UNIQUE (stat_date);


--
-- TOC entry 4976 (class 2606 OID 20300)
-- Name: data_sources data_sources_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_sources
    ADD CONSTRAINT data_sources_name_key UNIQUE (name);


--
-- TOC entry 4978 (class 2606 OID 20298)
-- Name: data_sources data_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_sources
    ADD CONSTRAINT data_sources_pkey PRIMARY KEY (id);


--
-- TOC entry 5034 (class 2606 OID 20521)
-- Name: market_analytics market_analytics_area_name_analysis_date_analysis_period_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_analytics
    ADD CONSTRAINT market_analytics_area_name_analysis_date_analysis_period_key UNIQUE (area_name, analysis_date, analysis_period);


--
-- TOC entry 5036 (class 2606 OID 20519)
-- Name: market_analytics market_analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_analytics
    ADD CONSTRAINT market_analytics_pkey PRIMARY KEY (id);


--
-- TOC entry 5007 (class 2606 OID 20363)
-- Name: price_history price_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.price_history
    ADD CONSTRAINT price_history_pkey PRIMARY KEY (id);


--
-- TOC entry 5004 (class 2606 OID 20342)
-- Name: properties properties_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.properties
    ADD CONSTRAINT properties_pkey PRIMARY KEY (id);


--
-- TOC entry 5020 (class 2606 OID 20421)
-- Name: property_views property_views_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_views
    ADD CONSTRAINT property_views_pkey PRIMARY KEY (id);


--
-- TOC entry 5031 (class 2606 OID 20494)
-- Name: saved_map_searches saved_map_searches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_map_searches
    ADD CONSTRAINT saved_map_searches_pkey PRIMARY KEY (id);


--
-- TOC entry 5026 (class 2606 OID 20464)
-- Name: shared_properties shared_properties_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shared_properties
    ADD CONSTRAINT shared_properties_pkey PRIMARY KEY (id);


--
-- TOC entry 5028 (class 2606 OID 20466)
-- Name: shared_properties shared_properties_share_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shared_properties
    ADD CONSTRAINT shared_properties_share_token_key UNIQUE (share_token);


--
-- TOC entry 5016 (class 1259 OID 20565)
-- Name: idx_client_favorites_property; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_client_favorites_property ON public.client_favorites USING btree (property_id);


--
-- TOC entry 5010 (class 1259 OID 20560)
-- Name: idx_clients_agent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clients_agent ON public.clients USING btree (agent_id);


--
-- TOC entry 5011 (class 1259 OID 20544)
-- Name: idx_clients_search_polygon; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clients_search_polygon ON public.clients USING gist (search_polygon);


--
-- TOC entry 5032 (class 1259 OID 20566)
-- Name: idx_market_analytics_area_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_market_analytics_area_date ON public.market_analytics USING btree (area_name, analysis_date);


--
-- TOC entry 5005 (class 1259 OID 20557)
-- Name: idx_price_history_property_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_price_history_property_date ON public.price_history USING btree (property_id, detected_at DESC);


--
-- TOC entry 4983 (class 1259 OID 20559)
-- Name: idx_properties_agent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_agent ON public.properties USING btree (managed_by_agent_id) WHERE (managed_by_agent_id IS NOT NULL);


--
-- TOC entry 4984 (class 1259 OID 20549)
-- Name: idx_properties_area; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_area ON public.properties USING btree (area_m2) WHERE (area_m2 IS NOT NULL);


--
-- TOC entry 4985 (class 1259 OID 20551)
-- Name: idx_properties_barrio; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_barrio ON public.properties USING btree (barrio) WHERE (barrio IS NOT NULL);


--
-- TOC entry 4986 (class 1259 OID 20550)
-- Name: idx_properties_bedrooms; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_bedrooms ON public.properties USING btree (bedrooms) WHERE (bedrooms IS NOT NULL);


--
-- TOC entry 4987 (class 1259 OID 20912)
-- Name: idx_properties_coords; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_coords ON public.properties USING btree (latitude, longitude);


--
-- TOC entry 4988 (class 1259 OID 20925)
-- Name: idx_properties_distancia_almar; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_distancia_almar ON public.properties USING btree (distancia_almar) WHERE (distancia_almar IS NOT NULL);


--
-- TOC entry 4989 (class 1259 OID 20552)
-- Name: idx_properties_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_estado ON public.properties USING btree (estado);


--
-- TOC entry 4990 (class 1259 OID 20679)
-- Name: idx_properties_inmobiliarias_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_inmobiliarias_gin ON public.properties USING gin (inmobiliarias_array);


--
-- TOC entry 4991 (class 1259 OID 20910)
-- Name: idx_properties_latitude; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_latitude ON public.properties USING btree (latitude);


--
-- TOC entry 4992 (class 1259 OID 20543)
-- Name: idx_properties_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_location ON public.properties USING gist (location);


--
-- TOC entry 4993 (class 1259 OID 20911)
-- Name: idx_properties_longitude; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_longitude ON public.properties USING btree (longitude);


--
-- TOC entry 4994 (class 1259 OID 20861)
-- Name: idx_properties_luminosidad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_luminosidad ON public.properties USING btree (luminosidad) WHERE (luminosidad IS NOT NULL);


--
-- TOC entry 4995 (class 1259 OID 20548)
-- Name: idx_properties_price_range; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_price_range ON public.properties USING btree (price, price_currency) WHERE (is_active = true);


--
-- TOC entry 4996 (class 1259 OID 20556)
-- Name: idx_properties_scraped_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_scraped_date ON public.properties USING btree (last_scraped_at, is_active);


--
-- TOC entry 4997 (class 1259 OID 20555)
-- Name: idx_properties_scraped_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_scraped_id ON public.properties USING btree (scraped_id, data_source_id);


--
-- TOC entry 4998 (class 1259 OID 20554)
-- Name: idx_properties_scraped_url; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_scraped_url ON public.properties USING btree (scraped_url);


--
-- TOC entry 4999 (class 1259 OID 20546)
-- Name: idx_properties_status_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_status_active ON public.properties USING btree (status, is_active);


--
-- TOC entry 5000 (class 1259 OID 20558)
-- Name: idx_properties_text_search; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_text_search ON public.properties USING gin (to_tsvector('spanish'::regconfig, ((COALESCE(title, ''::text) || ' '::text) || COALESCE(description, ''::text))));


--
-- TOC entry 5001 (class 1259 OID 20547)
-- Name: idx_properties_type_operation; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_properties_type_operation ON public.properties USING btree (property_type, tipo_operacion);


--
-- TOC entry 5002 (class 1259 OID 20680)
-- Name: idx_properties_unique_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_properties_unique_hash ON public.properties USING btree (property_unique_hash);


--
-- TOC entry 5017 (class 1259 OID 20564)
-- Name: idx_property_views_client; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_property_views_client ON public.property_views USING btree (client_id, viewed_at);


--
-- TOC entry 5018 (class 1259 OID 20563)
-- Name: idx_property_views_property; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_property_views_property ON public.property_views USING btree (property_id, viewed_at);


--
-- TOC entry 5029 (class 1259 OID 20545)
-- Name: idx_saved_searches_polygon; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_saved_searches_polygon ON public.saved_map_searches USING gist (search_polygon);


--
-- TOC entry 5023 (class 1259 OID 20561)
-- Name: idx_shared_properties_agent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_shared_properties_agent ON public.shared_properties USING btree (agent_id);


--
-- TOC entry 5024 (class 1259 OID 20562)
-- Name: idx_shared_properties_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_shared_properties_token ON public.shared_properties USING btree (share_token);


--
-- TOC entry 5055 (class 2620 OID 20572)
-- Name: agents update_agents_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON public.agents FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5058 (class 2620 OID 20574)
-- Name: clients update_clients_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON public.clients FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5056 (class 2620 OID 20576)
-- Name: properties update_days_on_market; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_days_on_market BEFORE INSERT OR UPDATE ON public.properties FOR EACH ROW EXECUTE FUNCTION public.calculate_days_on_market();


--
-- TOC entry 5059 (class 2620 OID 20578)
-- Name: client_favorites update_favorites_count; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_favorites_count AFTER INSERT OR DELETE ON public.client_favorites FOR EACH ROW EXECUTE FUNCTION public.update_property_counters();


--
-- TOC entry 5057 (class 2620 OID 20573)
-- Name: properties update_properties_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON public.properties FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5045 (class 2606 OID 20401)
-- Name: client_favorites client_favorites_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_favorites
    ADD CONSTRAINT client_favorites_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5046 (class 2606 OID 20406)
-- Name: client_favorites client_favorites_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_favorites
    ADD CONSTRAINT client_favorites_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- TOC entry 5050 (class 2606 OID 20446)
-- Name: client_searches client_searches_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_searches
    ADD CONSTRAINT client_searches_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5044 (class 2606 OID 20385)
-- Name: clients clients_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id) ON DELETE CASCADE;


--
-- TOC entry 5043 (class 2606 OID 20364)
-- Name: price_history price_history_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.price_history
    ADD CONSTRAINT price_history_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- TOC entry 5041 (class 2606 OID 20345)
-- Name: properties properties_data_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.properties
    ADD CONSTRAINT properties_data_source_id_fkey FOREIGN KEY (data_source_id) REFERENCES public.data_sources(id);


--
-- TOC entry 5042 (class 2606 OID 20350)
-- Name: properties properties_managed_by_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.properties
    ADD CONSTRAINT properties_managed_by_agent_id_fkey FOREIGN KEY (managed_by_agent_id) REFERENCES public.agents(id);


--
-- TOC entry 5047 (class 2606 OID 20432)
-- Name: property_views property_views_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_views
    ADD CONSTRAINT property_views_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- TOC entry 5048 (class 2606 OID 20427)
-- Name: property_views property_views_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_views
    ADD CONSTRAINT property_views_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5049 (class 2606 OID 20422)
-- Name: property_views property_views_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_views
    ADD CONSTRAINT property_views_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- TOC entry 5053 (class 2606 OID 20500)
-- Name: saved_map_searches saved_map_searches_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_map_searches
    ADD CONSTRAINT saved_map_searches_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- TOC entry 5054 (class 2606 OID 20495)
-- Name: saved_map_searches saved_map_searches_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_map_searches
    ADD CONSTRAINT saved_map_searches_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5051 (class 2606 OID 20472)
-- Name: shared_properties shared_properties_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shared_properties
    ADD CONSTRAINT shared_properties_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id) ON DELETE CASCADE;


--
-- TOC entry 5052 (class 2606 OID 20467)
-- Name: shared_properties shared_properties_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shared_properties
    ADD CONSTRAINT shared_properties_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- TOC entry 5220 (class 3256 OID 20570)
-- Name: client_favorites agent_client_favorites; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY agent_client_favorites ON public.client_favorites TO real_estate_app USING ((client_id IN ( SELECT clients.id
   FROM public.clients
  WHERE (clients.agent_id = (current_setting('app.current_agent_id'::text, true))::uuid))));


--
-- TOC entry 5218 (class 3256 OID 20568)
-- Name: clients agent_isolation; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY agent_isolation ON public.clients TO real_estate_app USING ((agent_id = (current_setting('app.current_agent_id'::text, true))::uuid));


--
-- TOC entry 5219 (class 3256 OID 20569)
-- Name: shared_properties agent_shared_properties; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY agent_shared_properties ON public.shared_properties TO real_estate_app USING ((agent_id = (current_setting('app.current_agent_id'::text, true))::uuid));


--
-- TOC entry 5214 (class 0 OID 20390)
-- Dependencies: 296
-- Name: client_favorites; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.client_favorites ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5213 (class 0 OID 20369)
-- Dependencies: 295
-- Name: clients; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5215 (class 0 OID 20411)
-- Dependencies: 297
-- Name: property_views; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.property_views ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5217 (class 0 OID 20477)
-- Dependencies: 300
-- Name: saved_map_searches; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.saved_map_searches ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5216 (class 0 OID 20451)
-- Dependencies: 299
-- Name: shared_properties; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.shared_properties ENABLE ROW LEVEL SECURITY;

-- Completed on 2025-06-15 22:41:35 UTC

--
-- PostgreSQL database dump complete
--

