"""
Sync Service
Automated synchronization between AoE4 World API and Supabase database
"""
from typing import List, Dict, Optional
from datetime import datetime
import logging

from ..api.aoe4world_client import AoE4WorldAPIClient
from ..database.supabase_client import SupabaseDBClient


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncService:
    """Service for syncing data from AoE4 World API to Supabase"""
    
    def __init__(self, 
                 api_client: Optional[AoE4WorldAPIClient] = None,
                 db_client: Optional[SupabaseDBClient] = None):
        """
        Initialize sync service
        
        Args:
            api_client: AoE4 World API client
            db_client: Supabase database client
        """
        self.api = api_client or AoE4WorldAPIClient()
        self.db = db_client or SupabaseDBClient()
    
    # ========================================================================
    # CIVILIZATION META STATS
    # ========================================================================
    
    def sync_civ_meta_stats(self, 
                           leaderboards: Optional[List[str]] = None,
                           rank_levels: Optional[List[str]] = None) -> int:
        """
        Sync civilization meta statistics from API to database
        
        Args:
            leaderboards: List of leaderboards to sync (defaults to all)
            rank_levels: List of rank levels to sync (defaults to all)
            
        Returns:
            Number of records synced
        """
        if leaderboards is None:
            leaderboards = ['rm_solo', 'rm_team', 'rm_1v1', 'rm_2v2', 'rm_3v3', 'rm_4v4']
        
        if rank_levels is None:
            rank_levels = ['all', 'bronze', 'silver', 'gold', 'platinum', 'diamond', 'conqueror']
        
        logger.info(f"Syncing civ meta stats for {len(leaderboards)} leaderboards and {len(rank_levels)} rank levels")
        
        all_stats = []
        
        for leaderboard in leaderboards:
            for rank_level in rank_levels:
                try:
                    logger.info(f"Fetching {leaderboard}/{rank_level}...")
                    stats = self.api.get_civ_stats(leaderboard, rank_level)
                    
                    for stat in stats:
                        # Map API response to database schema
                        db_record = {
                            'civ_id': self._normalize_civ_id(stat.get('civ_slug', '')),
                            'leaderboard': leaderboard,
                            'rank_level': rank_level,
                            'win_rate': stat.get('win_rate', 0),
                            'pick_rate': stat.get('pick_rate', 0),
                            'games_count': stat.get('games_count', 0),
                            'wins': stat.get('wins', 0),
                            'losses': stat.get('losses', 0),
                            'last_updated': datetime.utcnow().isoformat()
                        }
                        all_stats.append(db_record)
                    
                except Exception as e:
                    logger.error(f"Error syncing {leaderboard}/{rank_level}: {e}")
        
        if all_stats:
            logger.info(f"Upserting {len(all_stats)} records to database...")
            self.db.upsert_civ_meta_stats(all_stats)
            logger.info(f"✓ Synced {len(all_stats)} civ meta stat records")
        
        return len(all_stats)
    
    def sync_civ_meta_stats_quick(self) -> int:
        """
        Quick sync of most important civ meta stats (rm_solo, all ranks)
        
        Returns:
            Number of records synced
        """
        return self.sync_civ_meta_stats(
            leaderboards=['rm_solo'],
            rank_levels=['all']
        )
    
    # ========================================================================
    # LEADERBOARD
    # ========================================================================
    
    def sync_leaderboard(self, 
                        leaderboard: str = 'rm_solo',
                        count: int = 50) -> int:
        """
        Sync leaderboard players from API to database
        
        Args:
            leaderboard: Leaderboard type
            count: Number of players to sync
            
        Returns:
            Number of players synced
        """
        logger.info(f"Syncing top {count} players from {leaderboard}...")
        
        try:
            players = self.api.get_top_players(leaderboard, count)
            
            # Map API response to database schema
            db_records = []
            for player in players:
                db_record = {
                    'player_id': player.get('profile_id'),
                    'player_name': player.get('name', ''),
                    'rank': player.get('rank', 0),
                    'rating': player.get('rating', 0),
                    'games_count': player.get('games_count', 0),
                    'wins': player.get('wins', 0),
                    'losses': player.get('losses', 0),
                    'win_rate': player.get('win_rate', 0),
                    'leaderboard': leaderboard,
                    'last_updated': datetime.utcnow().isoformat()
                }
                db_records.append(db_record)
            
            if db_records:
                self.db.upsert_leaderboard_players(db_records)
                logger.info(f"✓ Synced {len(db_records)} players")
            
            return len(db_records)
            
        except Exception as e:
            logger.error(f"Error syncing leaderboard: {e}")
            return 0
    
    def sync_all_leaderboards(self, count: int = 50) -> Dict[str, int]:
        """
        Sync all leaderboards
        
        Args:
            count: Number of players per leaderboard
            
        Returns:
            Dictionary of leaderboard: count synced
        """
        leaderboards = ['rm_solo', 'rm_team', 'rm_1v1', 'rm_2v2', 'rm_3v3', 'rm_4v4']
        results = {}
        
        for leaderboard in leaderboards:
            results[leaderboard] = self.sync_leaderboard(leaderboard, count)
        
        return results
    
    # ========================================================================
    # FULL SYNC
    # ========================================================================
    
    def sync_all(self) -> Dict[str, int]:
        """
        Perform a full sync of all data
        
        Returns:
            Dictionary of sync results
        """
        logger.info("="*60)
        logger.info("FULL SYNC STARTED")
        logger.info("="*60)
        
        results = {}
        
        # Sync civ meta stats
        logger.info("\n[1/2] Syncing civilization meta stats...")
        results['civ_meta_stats'] = self.sync_civ_meta_stats()
        
        # Sync leaderboards
        logger.info("\n[2/2] Syncing leaderboards...")
        leaderboard_results = self.sync_all_leaderboards(count=50)
        results['leaderboards'] = leaderboard_results
        results['total_players'] = sum(leaderboard_results.values())
        
        logger.info("\n" + "="*60)
        logger.info("FULL SYNC COMPLETE")
        logger.info("="*60)
        logger.info(f"Civ meta stats: {results['civ_meta_stats']}")
        logger.info(f"Total players: {results['total_players']}")
        
        return results
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def _normalize_civ_id(self, civ_slug: str) -> str:
        """
        Normalize civilization slug to database ID format
        
        Args:
            civ_slug: Civilization slug from API
            
        Returns:
            Normalized civilization ID
        """
        # Map API slugs to database IDs
        civ_map = {
            'abbasid': 'abbasid',
            'ayyubids': 'ayyubids',
            'byzantines': 'byzantines',
            'chinese': 'chinese',
            'delhi': 'delhi',
            'english': 'english',
            'french': 'french',
            'hre': 'hre',
            'japanese': 'japanese',
            'malians': 'malians',
            'mongols': 'mongols',
            'ottomans': 'ottomans',
            'rus': 'rus',
            'golden-horde': 'golden_horde',
            'jeanne-darc': 'jeanne_darc',
            'lancaster': 'lancaster',
            'macedonian': 'macedonian',
            'order-of-the-dragon': 'order_of_the_dragon',
            'sengoku': 'sengoku',
            'templar': 'templar',
            'tughlaq': 'tughlaq',
            'zhu-xis-legacy': 'zhuxi'
        }
        
        return civ_map.get(civ_slug, civ_slug.replace('-', '_'))


# Convenience function
def create_sync_service(api_client: Optional[AoE4WorldAPIClient] = None,
                       db_client: Optional[SupabaseDBClient] = None) -> SyncService:
    """Create and return a sync service instance"""
    return SyncService(api_client=api_client, db_client=db_client)
