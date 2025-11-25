#!/usr/bin/env python3
"""
CLI script for syncing data from AoE4 World API to Supabase
"""
import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.sync.sync_service import create_sync_service


def main():
    parser = argparse.ArgumentParser(description='Sync AoE4 data from API to database')
    parser.add_argument('--mode', choices=['quick', 'full', 'civ-stats', 'leaderboard'],
                       default='quick',
                       help='Sync mode (default: quick)')
    parser.add_argument('--leaderboard', default='rm_solo',
                       help='Leaderboard to sync (default: rm_solo)')
    parser.add_argument('--count', type=int, default=50,
                       help='Number of players to sync (default: 50)')
    
    args = parser.parse_args()
    
    # Create sync service
    sync = create_sync_service()
    
    print(f"Starting sync in '{args.mode}' mode...")
    print()
    
    if args.mode == 'quick':
        # Quick sync: rm_solo meta stats + top 50 players
        sync.sync_civ_meta_stats_quick()
        sync.sync_leaderboard('rm_solo', 50)
        
    elif args.mode == 'full':
        # Full sync: all meta stats + all leaderboards
        sync.sync_all()
        
    elif args.mode == 'civ-stats':
        # Sync only civ meta stats
        sync.sync_civ_meta_stats()
        
    elif args.mode == 'leaderboard':
        # Sync specific leaderboard
        sync.sync_leaderboard(args.leaderboard, args.count)
    
    print()
    print("✓ Sync complete!")


if __name__ == '__main__':
    main()
