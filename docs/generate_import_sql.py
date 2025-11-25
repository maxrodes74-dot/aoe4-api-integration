#!/usr/bin/env python3.11
"""
Generate complete SQL import file for all AoE4 data
"""
import json
import glob

CIV_ID_MAP = {
    "abbasid": "abbasid", "ayyubids": "ayyubids", "byzantines": "byzantines",
    "chinese": "chinese", "delhi": "delhi", "english": "english",
    "french": "french", "goldenhorde": "golden_horde", "hre": "hre",
    "japanese": "japanese", "jeannedarc": "jeanne_darc", "lancaster": "lancaster",
    "macedonian": "macedonian", "malians": "malians", "mongols": "mongols",
    "orderofthedragon": "order_of_the_dragon", "ottomans": "ottomans",
    "rus": "rus", "sengoku": "sengoku", "templar": "templar",
    "tughlaq": "tughlaq", "zhuxi": "zhuxi"
}

CIV_NAME_MAP = {
    "abbasid": "Abbasid Dynasty", "ayyubids": "Ayyubids", "byzantines": "Byzantines",
    "chinese": "Chinese", "delhi": "Delhi Sultanate", "english": "English",
    "french": "French", "goldenhorde": "Golden Horde", "hre": "Holy Roman Empire",
    "japanese": "Japanese", "jeannedarc": "Jeanne d'Arc", "lancaster": "House of Lancaster",
    "macedonian": "Macedonian Dynasty", "malians": "Malians", "mongols": "Mongols",
    "orderofthedragon": "Order of the Dragon", "ottomans": "Ottomans",
    "rus": "Rus", "sengoku": "Sengoku Daimyo", "templar": "Knights Templar",
    "tughlaq": "Tughlaq Dynasty", "zhuxi": "Zhu Xi's Legacy"
}

def escape_sql(text):
    if not isinstance(text, str):
        return ''
    return text.replace("'", "''").replace("\\", "\\\\")[:1000]

output = open('/home/ubuntu/data/complete_import.sql', 'w')

output.write("-- Complete AoE4 Data Import\n")
output.write("-- Generated SQL for Supabase\n\n")

# Clear existing data
output.write("-- Clear existing data\n")
output.write("DELETE FROM civ_technologies;\n")
output.write("DELETE FROM civ_buildings;\n")
output.write("DELETE FROM civ_units;\n")
output.write("DELETE FROM base_technologies;\n")
output.write("DELETE FROM base_buildings;\n")
output.write("DELETE FROM base_units;\n")
output.write("DELETE FROM civilizations;\n\n")

# Import civilizations
output.write("-- Import Civilizations\n")
civ_files = glob.glob('/home/ubuntu/data/civilizations/*.json')
for file_path in sorted(civ_files):
    with open(file_path, 'r') as f:
        civ_data = json.load(f)
    
    civ_id_raw = file_path.split('/')[-1].replace('.json', '')
    civ_id = CIV_ID_MAP.get(civ_id_raw, civ_id_raw)
    name = CIV_NAME_MAP.get(civ_id_raw, civ_data.get('name', ''))
    description = escape_sql(civ_data.get('description', ''))
    overview_raw = civ_data.get('overview', '')
    overview = escape_sql(overview_raw) if isinstance(overview_raw, str) else ''
    
    output.write(f"INSERT INTO civilizations (id, name, description, overview) VALUES ('{civ_id}', '{name}', '{description}', '{overview}');\n")

output.write("\n")

# Import units
output.write("-- Import Base Units\n")
base_units = {}
unit_files = glob.glob('/home/ubuntu/data/units/*-unified.json')
for file_path in sorted(unit_files):
    with open(file_path, 'r') as f:
        file_data = json.load(f)
        units = file_data.get('data', [])
    
    for unit in units:
        unit_id = unit.get('id', '')
        if not unit_id or unit_id in base_units:
            continue
        
        name = escape_sql(unit.get('name', ''))
        description = escape_sql(unit.get('description', ''))
        
        base_units[unit_id] = True
        output.write(f"INSERT INTO base_units (id, name, description, type, icon_url) VALUES ('{unit_id}', '{name}', '{description}', 'unit', 'https://aoe4world.com/img/units/{unit_id}.png');\n")

output.write("\n-- Import Civ-Unit Mappings\n")
for file_path in sorted(unit_files):
    civ_id_raw = file_path.split('/')[-1].replace('-unified.json', '')
    civ_id = CIV_ID_MAP.get(civ_id_raw, civ_id_raw)
    
    with open(file_path, 'r') as f:
        file_data = json.load(f)
        units = file_data.get('data', [])
    
    for unit in units:
        unit_id = unit.get('id', '')
        if not unit_id or not unit.get('variations'):
            continue
        
        first_var = unit['variations'][0]
        costs = first_var.get('costs', {})
        movement = first_var.get('movement', {})
        unique = str(unit.get('unique', False)).lower()
        
        # Handle special resources: oliveoil and vizier count as gold equivalent
        cost_food = costs.get('food', 0)
        cost_wood = costs.get('wood', 0)
        cost_stone = costs.get('stone', 0)
        cost_gold = costs.get('gold', 0) + costs.get('oliveoil', 0) + costs.get('vizier', 0)
        
        output.write(f"INSERT INTO civ_units (civ_id, unit_id, unique_to_civ, age, cost_food, cost_wood, cost_stone, cost_gold, build_time, hitpoints, movement_speed) VALUES ('{civ_id}', '{unit_id}', {unique}, {first_var.get('age', 1)}, {cost_food}, {cost_wood}, {cost_stone}, {cost_gold}, {costs.get('time', 0)}, {first_var.get('hitpoints', 0)}, {movement.get('speed', 0) if movement else 0});\n")

# Import buildings
output.write("\n-- Import Base Buildings\n")
base_buildings = {}
building_files = glob.glob('/home/ubuntu/data/buildings/*-unified.json')
for file_path in sorted(building_files):
    with open(file_path, 'r') as f:
        file_data = json.load(f)
        buildings = file_data.get('data', [])
    
    for building in buildings:
        building_id = building.get('id', '')
        if not building_id or building_id in base_buildings:
            continue
        
        name = escape_sql(building.get('name', ''))
        description = escape_sql(building.get('description', ''))
        
        base_buildings[building_id] = True
        output.write(f"INSERT INTO base_buildings (id, name, description, type, icon_url) VALUES ('{building_id}', '{name}', '{description}', 'building', 'https://aoe4world.com/img/buildings/{building_id}.png');\n")

output.write("\n-- Import Civ-Building Mappings\n")
for file_path in sorted(building_files):
    civ_id_raw = file_path.split('/')[-1].replace('-unified.json', '')
    civ_id = CIV_ID_MAP.get(civ_id_raw, civ_id_raw)
    
    with open(file_path, 'r') as f:
        file_data = json.load(f)
        buildings = file_data.get('data', [])
    
    for building in buildings:
        building_id = building.get('id', '')
        if not building_id or not building.get('variations'):
            continue
        
        first_var = building['variations'][0]
        costs = first_var.get('costs', {})
        unique = str(building.get('unique', False)).lower()
        
        # Handle special resources
        cost_food = costs.get('food', 0)
        cost_wood = costs.get('wood', 0)
        cost_stone = costs.get('stone', 0)
        cost_gold = costs.get('gold', 0) + costs.get('oliveoil', 0) + costs.get('vizier', 0)
        
        output.write(f"INSERT INTO civ_buildings (civ_id, building_id, unique_to_civ, age, cost_food, cost_wood, cost_stone, cost_gold, build_time, hitpoints) VALUES ('{civ_id}', '{building_id}', {unique}, {first_var.get('age', 1)}, {cost_food}, {cost_wood}, {cost_stone}, {cost_gold}, {costs.get('time', 0)}, {first_var.get('hitpoints', 0)});\n")

# Import technologies
output.write("\n-- Import Base Technologies\n")
base_technologies = {}
tech_files = glob.glob('/home/ubuntu/data/technologies/*-unified.json')
for file_path in sorted(tech_files):
    with open(file_path, 'r') as f:
        file_data = json.load(f)
        technologies = file_data.get('data', [])
    
    for tech in technologies:
        tech_id = tech.get('id', '')
        if not tech_id or tech_id in base_technologies:
            continue
        
        name = escape_sql(tech.get('name', ''))
        description = escape_sql(tech.get('description', ''))
        
        base_technologies[tech_id] = True
        output.write(f"INSERT INTO base_technologies (id, name, description, type, icon_url) VALUES ('{tech_id}', '{name}', '{description}', 'technology', 'https://aoe4world.com/img/technologies/{tech_id}.png');\n")

output.write("\n-- Import Civ-Technology Mappings\n")
for file_path in sorted(tech_files):
    civ_id_raw = file_path.split('/')[-1].replace('-unified.json', '')
    civ_id = CIV_ID_MAP.get(civ_id_raw, civ_id_raw)
    
    with open(file_path, 'r') as f:
        file_data = json.load(f)
        technologies = file_data.get('data', [])
    
    for tech in technologies:
        tech_id = tech.get('id', '')
        if not tech_id:
            continue
        
        costs = tech.get('costs') or {}
        age = tech.get('age')
        age_val = age if age is not None else 'NULL'
        unique = str(tech.get('unique', False)).lower()
        
        # Handle special resources
        cost_food = costs.get('food', 0)
        cost_wood = costs.get('wood', 0)
        cost_stone = costs.get('stone', 0)
        cost_gold = costs.get('gold', 0) + costs.get('oliveoil', 0) + costs.get('vizier', 0)
        
        output.write(f"INSERT INTO civ_technologies (civ_id, technology_id, unique_to_civ, age, cost_food, cost_wood, cost_stone, cost_gold, research_time) VALUES ('{civ_id}', '{tech_id}', {unique}, {age_val}, {cost_food}, {cost_wood}, {cost_stone}, {cost_gold}, {costs.get('time', 0)});\n")

output.close()

print("✓ Generated /home/ubuntu/data/complete_import.sql")
print(f"  Civilizations: {len(CIV_ID_MAP)}")
print(f"  Base Units: {len(base_units)}")
print(f"  Base Buildings: {len(base_buildings)}")
print(f"  Base Technologies: {len(base_technologies)}")
