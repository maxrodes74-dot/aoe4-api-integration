# AoE4 API Integration

Comprehensive Python library for integrating Age of Empires IV data from the AoE4 World API into a Supabase database, with support for automated syncing, querying, and AI-powered analysis.

## Features

✅ **Complete AoE4 World API Client** - Access all endpoints (stats, leaderboards, players, matches)  
✅ **Supabase Database Integration** - Full CRUD operations with relational queries  
✅ **Automated Sync Service** - Keep your database up-to-date with live competitive data  
✅ **Civilization Meta Stats** - Track win rates, pick rates across all leaderboards and ranks  
✅ **Leaderboard Tracking** - Monitor top players and their performance  
✅ **Type-Safe** - Clean, well-documented Python code  
✅ **CLI Tools** - Command-line scripts for manual operations  

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/aoe4-api-integration.git
cd aoe4-api-integration

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials
```

### Basic Usage

```python
from src.api.aoe4world_client import create_client
from src.database.supabase_client import create_db_client
from src.sync.sync_service import create_sync_service

# Get live data from API
api = create_client()
civ_stats = api.get_civ_stats('rm_solo', 'all')

# Query database
db = create_db_client()
units = db.get_units_for_civ('english')

# Sync data
sync = create_sync_service()
sync.sync_all()
```

See full documentation in the repository for detailed usage, API reference, and examples.

## Project Structure

- `src/api/` - AoE4 World API client
- `src/database/` - Supabase database client  
- `src/sync/` - Automated sync service
- `scripts/` - CLI tools
- `examples/` - Usage examples

## License

MIT License
