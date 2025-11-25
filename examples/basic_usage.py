"""
Basic Usage Examples
Demonstrates how to use the AoE4 API integration
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.aoe4world_client import create_client as create_api_client
from src.database.supabase_client import create_db_client
from src.sync.sync_service import create_sync_service


def example_api_client():
    """Example: Using the AoE4 World API client"""
    print("="*60)
    print("EXAMPLE: AoE4 World API Client")
    print("="*60)
    
    # Create API client
    api = create_api_client()
    
    # Get civilization statistics
    print("\n1. Getting civilization statistics...")
    civ_stats = api.get_civ_stats('rm_solo', 'all')
    print(f"   Found {len(civ_stats)} civilizations")
    
    # Show top 3
    sorted_stats = sorted(civ_stats, key=lambda x: x.get('win_rate', 0), reverse=True)
    print("\n   Top 3 civilizations by win rate:")
    for i, civ in enumerate(sorted_stats[:3], 1):
        print(f"   {i}. {civ.get('civ_name')}: {civ.get('win_rate')}% WR, {civ.get('pick_rate')}% PR")
    
    # Get leaderboard
    print("\n2. Getting leaderboard...")
    players = api.get_top_players('rm_solo', 10)
    print(f"   Found {len(players)} players")
    print(f"\n   #1 Player: {players[0].get('name')} - {players[0].get('rating')} ELO")


def example_database_client():
    """Example: Using the Supabase database client"""
    print("\n" + "="*60)
    print("EXAMPLE: Supabase Database Client")
    print("="*60)
    
    # Create database client (requires SUPABASE_URL and SUPABASE_KEY env vars)
    try:
        db = create_db_client()
        
        # Get all civilizations
        print("\n1. Getting civilizations from database...")
        civs = db.get_civilizations()
        print(f"   Found {len(civs)} civilizations")
        
        # Get units for English
        print("\n2. Getting English units...")
        units = db.get_units_for_civ('english')
        print(f"   English has {len(units)} units")
        
        # Get unique units
        unique_units = db.get_unique_units_for_civ('english')
        print(f"   English has {len(unique_units)} unique units")
        
        # Get meta stats
        print("\n3. Getting current meta stats...")
        meta_stats = db.get_top_civs_by_winrate('rm_solo', 'all', 5)
        print(f"   Top 5 civilizations:")
        for i, stat in enumerate(meta_stats, 1):
            civ_name = stat.get('civilizations', {}).get('name', 'Unknown')
            print(f"   {i}. {civ_name}: {stat.get('win_rate')}% WR")
        
    except ValueError as e:
        print(f"\n   ⚠️  Database client requires SUPABASE_URL and SUPABASE_KEY environment variables")
        print(f"   Error: {e}")


def example_sync_service():
    """Example: Using the sync service"""
    print("\n" + "="*60)
    print("EXAMPLE: Sync Service")
    print("="*60)
    
    try:
        # Create sync service
        sync = create_sync_service()
        
        # Quick sync
        print("\n1. Running quick sync (rm_solo meta stats)...")
        count = sync.sync_civ_meta_stats_quick()
        print(f"   ✓ Synced {count} records")
        
        # Sync leaderboard
        print("\n2. Syncing top 10 players...")
        count = sync.sync_leaderboard('rm_solo', 10)
        print(f"   ✓ Synced {count} players")
        
    except ValueError as e:
        print(f"\n   ⚠️  Sync service requires SUPABASE_URL and SUPABASE_KEY environment variables")
        print(f"   Error: {e}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" AoE4 API Integration - Basic Usage Examples")
    print("="*70)
    
    # Example 1: API Client (no credentials needed)
    example_api_client()
    
    # Example 2: Database Client (requires Supabase credentials)
    example_database_client()
    
    # Example 3: Sync Service (requires Supabase credentials)
    example_sync_service()
    
    print("\n" + "="*70)
    print(" Examples complete!")
    print("="*70)


if __name__ == '__main__':
    main()
