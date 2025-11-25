# API Reference

Complete reference for all modules and functions in the AoE4 API Integration library.

## Table of Contents

1. [AoE4 World API Client](#aoe4-world-api-client)
2. [Supabase Database Client](#supabase-database-client)
3. [Sync Service](#sync-service)

---

## AoE4 World API Client

### `AoE4WorldAPIClient`

Client for interacting with the AoE4 World API.

#### Initialization

```python
from src.api.aoe4world_client import AoE4WorldAPIClient

client = AoE4WorldAPIClient(rate_limit_delay=0.5)
```

**Parameters:**
- `rate_limit_delay` (float): Delay between requests in seconds (default: 0.5)

#### Methods

##### Civilization Statistics

**`get_civ_stats(leaderboard='rm_solo', rank_level='all')`**

Get civilization statistics for a specific leaderboard and rank level.

**Parameters:**
- `leaderboard` (str): Leaderboard type (`rm_solo`, `rm_team`, `rm_1v1`, `rm_2v2`, `rm_3v3`, `rm_4v4`)
- `rank_level` (str): Rank level (`all`, `bronze`, `silver`, `gold`, `platinum`, `diamond`, `conqueror`)

**Returns:** List[Dict] - List of civilization statistics

**Example:**
```python
stats = client.get_civ_stats('rm_solo', 'diamond')
for stat in stats:
    print(f"{stat['civ_name']}: {stat['win_rate']}% WR")
```

**`get_all_civ_stats()`**

Get civilization statistics for all leaderboards and rank levels.

**Returns:** List[Dict] - All civilization statistics with metadata

##### Leaderboards

**`get_leaderboard(leaderboard='rm_solo', count=50, page=1)`**

Get leaderboard rankings.

**Parameters:**
- `leaderboard` (str): Leaderboard type
- `count` (int): Number of results per page (max 200)
- `page` (int): Page number

**Returns:** Dict - Leaderboard data with players

**`get_top_players(leaderboard='rm_solo', count=50)`**

Get top players from a leaderboard.

**Parameters:**
- `leaderboard` (str): Leaderboard type
- `count` (int): Number of players to fetch

**Returns:** List[Dict] - List of player data

##### Players

**`get_player(player_id)`**

Get player profile.

**Parameters:**
- `player_id` (int): Player ID

**Returns:** Dict - Player profile data

**`search_players(query)`**

Search for players by name.

**Parameters:**
- `query` (str): Search query (player name)

**Returns:** List[Dict] - List of matching players

**`get_player_games(player_id, count=20, page=1)`**

Get recent games for a player.

**Parameters:**
- `player_id` (int): Player ID
- `count` (int): Number of games per page
- `page` (int): Page number

**Returns:** List[Dict] - List of game data

##### Matches

**`get_game(game_id)`**

Get detailed game/match data.

**Parameters:**
- `game_id` (int): Game ID

**Returns:** Dict - Detailed game data

##### Maps

**`get_map_stats(leaderboard='rm_solo')`**

Get map statistics.

**Parameters:**
- `leaderboard` (str): Leaderboard type

**Returns:** List[Dict] - List of map statistics

---

## Supabase Database Client

### `SupabaseDBClient`

Client for interacting with the Supabase database.

#### Initialization

```python
from src.database.supabase_client import SupabaseDBClient

client = SupabaseDBClient(url='https://...', key='...')
# Or use environment variables:
client = SupabaseDBClient()  # Uses SUPABASE_URL and SUPABASE_KEY
```

**Parameters:**
- `url` (str, optional): Supabase project URL
- `key` (str, optional): Supabase API key

#### Methods

##### Civilizations

**`get_civilizations()`**

Get all civilizations.

**Returns:** List[Dict] - All civilizations

**`get_civilization(civ_id)`**

Get a specific civilization by ID.

**Parameters:**
- `civ_id` (str): Civilization ID (e.g., 'english', 'french')

**Returns:** Dict | None - Civilization data

##### Units

**`get_units_for_civ(civ_id)`**

Get all units for a civilization with full details.

**Parameters:**
- `civ_id` (str): Civilization ID

**Returns:** List[Dict] - Units with stats

**`get_unit_comparison(unit_id)`**

Compare a unit across all civilizations.

**Parameters:**
- `unit_id` (str): Base unit ID (e.g., 'man-at-arms')

**Returns:** List[Dict] - Civ-specific unit stats

**`get_unique_units_for_civ(civ_id)`**

Get unique units for a civilization.

**Parameters:**
- `civ_id` (str): Civilization ID

**Returns:** List[Dict] - Unique units

##### Buildings

**`get_buildings_for_civ(civ_id)`**

Get all buildings for a civilization.

**Parameters:**
- `civ_id` (str): Civilization ID

**Returns:** List[Dict] - Buildings with stats

**`get_unique_buildings_for_civ(civ_id)`**

Get unique buildings for a civilization.

**Parameters:**
- `civ_id` (str): Civilization ID

**Returns:** List[Dict] - Unique buildings

##### Technologies

**`get_technologies_for_civ(civ_id)`**

Get all technologies for a civilization.

**Parameters:**
- `civ_id` (str): Civilization ID

**Returns:** List[Dict] - Technologies

**`get_unique_technologies_for_civ(civ_id)`**

Get unique technologies for a civilization.

**Parameters:**
- `civ_id` (str): Civilization ID

**Returns:** List[Dict] - Unique technologies

##### Meta Stats

**`upsert_civ_meta_stats(stats)`**

Insert or update civilization meta statistics.

**Parameters:**
- `stats` (List[Dict]): List of stat dictionaries

**`get_civ_meta_stats(leaderboard='rm_solo', rank_level='all')`**

Get civilization meta statistics.

**Parameters:**
- `leaderboard` (str): Leaderboard type
- `rank_level` (str): Rank level

**Returns:** List[Dict] - Meta stats with civilization names

**`get_top_civs_by_winrate(leaderboard='rm_solo', rank_level='all', limit=10)`**

Get top civilizations by win rate.

**Parameters:**
- `leaderboard` (str): Leaderboard type
- `rank_level` (str): Rank level
- `limit` (int): Number of civilizations

**Returns:** List[Dict] - Top civilizations

##### Leaderboard

**`upsert_leaderboard_players(players)`**

Insert or update leaderboard players.

**Parameters:**
- `players` (List[Dict]): List of player dictionaries

**`get_leaderboard_players(leaderboard='rm_solo', limit=50)`**

Get leaderboard players.

**Parameters:**
- `leaderboard` (str): Leaderboard type
- `limit` (int): Number of players

**Returns:** List[Dict] - Players ordered by rank

---

## Sync Service

### `SyncService`

Service for syncing data from AoE4 World API to Supabase.

#### Initialization

```python
from src.sync.sync_service import SyncService

service = SyncService(api_client=None, db_client=None)
# Or use defaults:
service = SyncService()  # Creates clients automatically
```

**Parameters:**
- `api_client` (AoE4WorldAPIClient, optional): API client instance
- `db_client` (SupabaseDBClient, optional): Database client instance

#### Methods

**`sync_civ_meta_stats(leaderboards=None, rank_levels=None)`**

Sync civilization meta statistics.

**Parameters:**
- `leaderboards` (List[str], optional): List of leaderboards (defaults to all)
- `rank_levels` (List[str], optional): List of rank levels (defaults to all)

**Returns:** int - Number of records synced

**`sync_civ_meta_stats_quick()`**

Quick sync of rm_solo meta stats (all ranks).

**Returns:** int - Number of records synced

**`sync_leaderboard(leaderboard='rm_solo', count=50)`**

Sync leaderboard players.

**Parameters:**
- `leaderboard` (str): Leaderboard type
- `count` (int): Number of players to sync

**Returns:** int - Number of players synced

**`sync_all_leaderboards(count=50)`**

Sync all leaderboards.

**Parameters:**
- `count` (int): Number of players per leaderboard

**Returns:** Dict[str, int] - Dictionary of leaderboard: count synced

**`sync_all()`**

Perform a full sync of all data.

**Returns:** Dict[str, int] - Dictionary of sync results

---

## Data Structures

### Civilization Stat

```python
{
    'civ_id': 'english',
    'civ_name': 'English',
    'civ_slug': 'english',
    'win_rate': 52.5,
    'pick_rate': 8.3,
    'games_count': 12345,
    'wins': 6481,
    'losses': 5864,
    'leaderboard': 'rm_solo',
    'rank_level': 'all'
}
```

### Player

```python
{
    'player_id': 12345,
    'profile_id': 12345,
    'name': 'PlayerName',
    'rank': 1,
    'rating': 2315,
    'games_count': 500,
    'wins': 300,
    'losses': 200,
    'win_rate': 60.0,
    'leaderboard': 'rm_solo'
}
```

### Unit

```python
{
    'unit_id': 'man-at-arms',
    'unit_name': 'Man-at-Arms',
    'civ_id': 'english',
    'civ_name': 'English',
    'unique_to_civ': False,
    'age': 1,
    'cost_food': 100,
    'cost_wood': 0,
    'cost_stone': 0,
    'cost_gold': 20,
    'cost_total': 120,
    'build_time': 22,
    'hitpoints': 155,
    'movement_speed': 1.12
}
```

---

## Error Handling

All methods may raise the following exceptions:

- `ValueError`: Invalid parameters or missing configuration
- `requests.HTTPError`: API request failed
- `Exception`: Database operation failed

Example error handling:

```python
try:
    stats = client.get_civ_stats('rm_solo', 'all')
except requests.HTTPError as e:
    print(f"API request failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Rate Limiting

The API client implements automatic rate limiting to avoid overwhelming the AoE4 World API:

- Default delay: 0.5 seconds between requests
- Configurable via `rate_limit_delay` parameter
- Automatically enforced for all API calls

---

## Best Practices

1. **Use environment variables** for credentials
2. **Implement error handling** for all API calls
3. **Respect rate limits** - don't decrease delay below 0.5s
4. **Cache results** when appropriate
5. **Use quick sync** for frequent updates
6. **Use full sync** sparingly (daily at most)

---

For more examples, see the `examples/` directory.
