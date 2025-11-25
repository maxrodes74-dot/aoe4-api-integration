-- AoE4 Stats Database Schema
-- Properly structured relational database with civ-specific mappings

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Civilizations
CREATE TABLE civilizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    classes TEXT[],
    overview TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_civilizations_name ON civilizations(name);

-- ============================================================================
-- BASE ENTITY TABLES (shared definitions)
-- ============================================================================

-- Base Units (generic unit definitions shared across civs)
CREATE TABLE base_units (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT, -- infantry, cavalry, siege, naval, etc.
    display_classes TEXT[],
    icon_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_base_units_name ON base_units(name);
CREATE INDEX idx_base_units_type ON base_units(type);

-- Base Buildings
CREATE TABLE base_buildings (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT, -- economic, military, defensive, landmark
    display_classes TEXT[],
    icon_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_base_buildings_name ON base_buildings(name);
CREATE INDEX idx_base_buildings_type ON base_buildings(type);

-- Base Technologies
CREATE TABLE base_technologies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT, -- economic, military, unique
    icon_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_base_technologies_name ON base_technologies(name);

-- ============================================================================
-- JUNCTION TABLES (civ-specific instances with stats)
-- ============================================================================

-- Civ Units (which civs have which units, with civ-specific stats)
CREATE TABLE civ_units (
    id SERIAL PRIMARY KEY,
    civ_id TEXT NOT NULL REFERENCES civilizations(id) ON DELETE CASCADE,
    unit_id TEXT NOT NULL REFERENCES base_units(id) ON DELETE CASCADE,
    unique_to_civ BOOLEAN DEFAULT FALSE,
    age INTEGER NOT NULL CHECK (age >= 1 AND age <= 4),
    
    -- Costs
    cost_food INTEGER DEFAULT 0,
    cost_wood INTEGER DEFAULT 0,
    cost_stone INTEGER DEFAULT 0,
    cost_gold INTEGER DEFAULT 0,
    cost_total INTEGER GENERATED ALWAYS AS (cost_food + cost_wood + cost_stone + cost_gold) STORED,
    
    -- Production
    build_time NUMERIC(10, 2) DEFAULT 0,
    
    -- Stats
    hitpoints INTEGER DEFAULT 0,
    movement_speed NUMERIC(10, 3) DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(civ_id, unit_id)
);

CREATE INDEX idx_civ_units_civ ON civ_units(civ_id);
CREATE INDEX idx_civ_units_unit ON civ_units(unit_id);
CREATE INDEX idx_civ_units_unique ON civ_units(unique_to_civ) WHERE unique_to_civ = TRUE;
CREATE INDEX idx_civ_units_age ON civ_units(age);

-- Civ Buildings
CREATE TABLE civ_buildings (
    id SERIAL PRIMARY KEY,
    civ_id TEXT NOT NULL REFERENCES civilizations(id) ON DELETE CASCADE,
    building_id TEXT NOT NULL REFERENCES base_buildings(id) ON DELETE CASCADE,
    unique_to_civ BOOLEAN DEFAULT FALSE,
    age INTEGER NOT NULL CHECK (age >= 1 AND age <= 4),
    
    -- Costs
    cost_food INTEGER DEFAULT 0,
    cost_wood INTEGER DEFAULT 0,
    cost_stone INTEGER DEFAULT 0,
    cost_gold INTEGER DEFAULT 0,
    cost_total INTEGER GENERATED ALWAYS AS (cost_food + cost_wood + cost_stone + cost_gold) STORED,
    
    -- Production
    build_time NUMERIC(10, 2) DEFAULT 0,
    
    -- Stats
    hitpoints INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(civ_id, building_id)
);

CREATE INDEX idx_civ_buildings_civ ON civ_buildings(civ_id);
CREATE INDEX idx_civ_buildings_building ON civ_buildings(building_id);
CREATE INDEX idx_civ_buildings_unique ON civ_buildings(unique_to_civ) WHERE unique_to_civ = TRUE;
CREATE INDEX idx_civ_buildings_age ON civ_buildings(age);

-- Civ Technologies
CREATE TABLE civ_technologies (
    id SERIAL PRIMARY KEY,
    civ_id TEXT NOT NULL REFERENCES civilizations(id) ON DELETE CASCADE,
    technology_id TEXT NOT NULL REFERENCES base_technologies(id) ON DELETE CASCADE,
    unique_to_civ BOOLEAN DEFAULT FALSE,
    age INTEGER CHECK (age >= 1 AND age <= 4),
    
    -- Costs
    cost_food INTEGER DEFAULT 0,
    cost_wood INTEGER DEFAULT 0,
    cost_stone INTEGER DEFAULT 0,
    cost_gold INTEGER DEFAULT 0,
    cost_total INTEGER GENERATED ALWAYS AS (cost_food + cost_wood + cost_stone + cost_gold) STORED,
    
    -- Research
    research_time NUMERIC(10, 2) DEFAULT 0,
    
    -- Effects
    effects TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(civ_id, technology_id)
);

CREATE INDEX idx_civ_technologies_civ ON civ_technologies(civ_id);
CREATE INDEX idx_civ_technologies_tech ON civ_technologies(technology_id);
CREATE INDEX idx_civ_technologies_unique ON civ_technologies(unique_to_civ) WHERE unique_to_civ = TRUE;
CREATE INDEX idx_civ_technologies_age ON civ_technologies(age);

-- ============================================================================
-- LIVE API DATA TABLES
-- ============================================================================

-- Civilization Meta Stats (from AoE4 World API)
CREATE TABLE civilization_meta_stats (
    id SERIAL PRIMARY KEY,
    civ_id TEXT REFERENCES civilizations(id) ON DELETE CASCADE,
    leaderboard TEXT NOT NULL, -- rm_solo, rm_team
    rank_level TEXT, -- conqueror, diamond, etc.
    win_rate NUMERIC(5, 2),
    pick_rate NUMERIC(5, 2),
    games_count INTEGER,
    avg_game_duration INTEGER,
    patch TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(civ_id, leaderboard, rank_level)
);

CREATE INDEX idx_meta_stats_civ ON civilization_meta_stats(civ_id);
CREATE INDEX idx_meta_stats_leaderboard ON civilization_meta_stats(leaderboard);
CREATE INDEX idx_meta_stats_updated ON civilization_meta_stats(last_updated DESC);

-- Leaderboard Players
CREATE TABLE leaderboard_players (
    id SERIAL PRIMARY KEY,
    player_name TEXT NOT NULL,
    profile_id BIGINT UNIQUE,
    rank INTEGER,
    rating INTEGER,
    rank_level TEXT,
    win_rate NUMERIC(5, 2),
    games_count INTEGER,
    leaderboard TEXT NOT NULL,
    country TEXT,
    last_game TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_players_rank ON leaderboard_players(rank);
CREATE INDEX idx_players_rating ON leaderboard_players(rating DESC);
CREATE INDEX idx_players_leaderboard ON leaderboard_players(leaderboard);

-- ============================================================================
-- AI ANALYSIS TABLES
-- ============================================================================

-- Build Orders
CREATE TABLE build_orders (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    civ_id TEXT REFERENCES civilizations(id) ON DELETE CASCADE,
    strategy_type TEXT, -- rush, boom, turtle, etc.
    description TEXT,
    steps TEXT,
    total_time_seconds INTEGER,
    villager_count INTEGER,
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_build_orders_civ ON build_orders(civ_id);
CREATE INDEX idx_build_orders_strategy ON build_orders(strategy_type);
CREATE INDEX idx_build_orders_ai ON build_orders(ai_generated) WHERE ai_generated = TRUE;

-- Strategy Analysis
CREATE TABLE strategy_analysis (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    civ_id TEXT REFERENCES civilizations(id) ON DELETE CASCADE,
    matchup_vs TEXT,
    map_type TEXT, -- open, closed, water, hybrid
    early_game TEXT,
    mid_game TEXT,
    late_game TEXT,
    key_units TEXT,
    key_technologies TEXT,
    ai_confidence INTEGER CHECK (ai_confidence >= 0 AND ai_confidence <= 100),
    ai_reasoning TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_strategy_civ ON strategy_analysis(civ_id);
CREATE INDEX idx_strategy_map ON strategy_analysis(map_type);

-- ============================================================================
-- USEFUL VIEWS
-- ============================================================================

-- View: All units for a civilization with full details
CREATE VIEW v_civ_units_full AS
SELECT 
    c.id AS civ_id,
    c.name AS civ_name,
    bu.id AS unit_id,
    bu.name AS unit_name,
    bu.type AS unit_type,
    cu.unique_to_civ,
    cu.age,
    cu.cost_food,
    cu.cost_wood,
    cu.cost_stone,
    cu.cost_gold,
    cu.cost_total,
    cu.build_time,
    cu.hitpoints,
    cu.movement_speed,
    bu.icon_url
FROM civ_units cu
JOIN civilizations c ON cu.civ_id = c.id
JOIN base_units bu ON cu.unit_id = bu.id;

-- View: All buildings for a civilization
CREATE VIEW v_civ_buildings_full AS
SELECT 
    c.id AS civ_id,
    c.name AS civ_name,
    bb.id AS building_id,
    bb.name AS building_name,
    bb.type AS building_type,
    cb.unique_to_civ,
    cb.age,
    cb.cost_food,
    cb.cost_wood,
    cb.cost_stone,
    cb.cost_gold,
    cb.cost_total,
    cb.build_time,
    cb.hitpoints,
    bb.icon_url
FROM civ_buildings cb
JOIN civilizations c ON cb.civ_id = c.id
JOIN base_buildings bb ON cb.building_id = bb.id;

-- View: All technologies for a civilization
CREATE VIEW v_civ_technologies_full AS
SELECT 
    c.id AS civ_id,
    c.name AS civ_name,
    bt.id AS technology_id,
    bt.name AS technology_name,
    bt.type AS technology_type,
    ct.unique_to_civ,
    ct.age,
    ct.cost_food,
    ct.cost_wood,
    ct.cost_stone,
    ct.cost_gold,
    ct.cost_total,
    ct.research_time,
    ct.effects,
    bt.icon_url
FROM civ_technologies ct
JOIN civilizations c ON ct.civ_id = c.id
JOIN base_technologies bt ON ct.technology_id = bt.id;

-- View: Civilization summary with counts
CREATE VIEW v_civilization_summary AS
SELECT 
    c.id,
    c.name,
    c.description,
    COUNT(DISTINCT cu.unit_id) AS total_units,
    COUNT(DISTINCT cu.unit_id) FILTER (WHERE cu.unique_to_civ = TRUE) AS unique_units,
    COUNT(DISTINCT cb.building_id) AS total_buildings,
    COUNT(DISTINCT cb.building_id) FILTER (WHERE cb.unique_to_civ = TRUE) AS unique_buildings,
    COUNT(DISTINCT ct.technology_id) AS total_technologies,
    COUNT(DISTINCT ct.technology_id) FILTER (WHERE ct.unique_to_civ = TRUE) AS unique_technologies
FROM civilizations c
LEFT JOIN civ_units cu ON c.id = cu.civ_id
LEFT JOIN civ_buildings cb ON c.id = cb.civ_id
LEFT JOIN civ_technologies ct ON c.id = ct.civ_id
GROUP BY c.id, c.name, c.description;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_civilizations_updated_at BEFORE UPDATE ON civilizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_base_units_updated_at BEFORE UPDATE ON base_units
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_base_buildings_updated_at BEFORE UPDATE ON base_buildings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_base_technologies_updated_at BEFORE UPDATE ON base_technologies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_civ_units_updated_at BEFORE UPDATE ON civ_units
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_civ_buildings_updated_at BEFORE UPDATE ON civ_buildings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_civ_technologies_updated_at BEFORE UPDATE ON civ_technologies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_build_orders_updated_at BEFORE UPDATE ON build_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategy_analysis_updated_at BEFORE UPDATE ON strategy_analysis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE civilizations IS 'All Age of Empires 4 civilizations';
COMMENT ON TABLE base_units IS 'Base unit definitions shared across civilizations';
COMMENT ON TABLE base_buildings IS 'Base building definitions shared across civilizations';
COMMENT ON TABLE base_technologies IS 'Base technology definitions shared across civilizations';
COMMENT ON TABLE civ_units IS 'Junction table mapping civilizations to units with civ-specific stats';
COMMENT ON TABLE civ_buildings IS 'Junction table mapping civilizations to buildings with civ-specific stats';
COMMENT ON TABLE civ_technologies IS 'Junction table mapping civilizations to technologies with civ-specific stats';
COMMENT ON TABLE civilization_meta_stats IS 'Live competitive statistics from AoE4 World API';
COMMENT ON TABLE leaderboard_players IS 'Top players from competitive leaderboards';
COMMENT ON TABLE build_orders IS 'Build orders including AI-generated strategies';
COMMENT ON TABLE strategy_analysis IS 'Strategic analysis including AI-powered insights';
