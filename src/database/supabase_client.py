"""
Supabase Database Client
Client for interacting with the AoE4 Stats Supabase database
"""
import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client


class SupabaseDBClient:
    """Client for Supabase database operations"""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase client
        
        Args:
            url: Supabase project URL (defaults to SUPABASE_URL env var)
            key: Supabase API key (defaults to SUPABASE_KEY env var)
        """
        self.url = url or os.environ.get('SUPABASE_URL')
        self.key = key or os.environ.get('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and KEY must be provided or set in environment variables")
        
        self.client: Client = create_client(self.url, self.key)
    
    # ========================================================================
    # CIVILIZATIONS
    # ========================================================================
    
    def get_civilizations(self) -> List[Dict]:
        """Get all civilizations"""
        response = self.client.table('civilizations').select('*').execute()
        return response.data
    
    def get_civilization(self, civ_id: str) -> Optional[Dict]:
        """Get a specific civilization by ID"""
        response = self.client.table('civilizations').select('*').eq('id', civ_id).execute()
        return response.data[0] if response.data else None
    
    # ========================================================================
    # UNITS
    # ========================================================================
    
    def get_units_for_civ(self, civ_id: str) -> List[Dict]:
        """
        Get all units for a civilization with full details
        
        Uses the v_civ_units_full view
        """
        response = (self.client.table('v_civ_units_full')
                   .select('*')
                   .eq('civ_id', civ_id)
                   .execute())
        return response.data
    
    def get_unit_comparison(self, unit_id: str) -> List[Dict]:
        """
        Compare a unit across all civilizations
        
        Args:
            unit_id: Base unit ID
            
        Returns:
            List of civ-specific unit stats
        """
        response = (self.client.table('civ_units')
                   .select('*, civilizations(name), base_units(name)')
                   .eq('unit_id', unit_id)
                   .execute())
        return response.data
    
    def get_unique_units_for_civ(self, civ_id: str) -> List[Dict]:
        """Get unique units for a civilization"""
        response = (self.client.table('v_civ_units_full')
                   .select('*')
                   .eq('civ_id', civ_id)
                   .eq('unique_to_civ', True)
                   .execute())
        return response.data
    
    # ========================================================================
    # BUILDINGS
    # ========================================================================
    
    def get_buildings_for_civ(self, civ_id: str) -> List[Dict]:
        """Get all buildings for a civilization"""
        response = (self.client.table('v_civ_buildings_full')
                   .select('*')
                   .eq('civ_id', civ_id)
                   .execute())
        return response.data
    
    def get_unique_buildings_for_civ(self, civ_id: str) -> List[Dict]:
        """Get unique buildings for a civilization"""
        response = (self.client.table('v_civ_buildings_full')
                   .select('*')
                   .eq('civ_id', civ_id)
                   .eq('unique_to_civ', True)
                   .execute())
        return response.data
    
    # ========================================================================
    # TECHNOLOGIES
    # ========================================================================
    
    def get_technologies_for_civ(self, civ_id: str) -> List[Dict]:
        """Get all technologies for a civilization"""
        response = (self.client.table('v_civ_technologies_full')
                   .select('*')
                   .eq('civ_id', civ_id)
                   .execute())
        return response.data
    
    def get_unique_technologies_for_civ(self, civ_id: str) -> List[Dict]:
        """Get unique technologies for a civilization"""
        response = (self.client.table('v_civ_technologies_full')
                   .select('*')
                   .eq('civ_id', civ_id)
                   .eq('unique_to_civ', True)
                   .execute())
        return response.data
    
    # ========================================================================
    # META STATS
    # ========================================================================
    
    def upsert_civ_meta_stats(self, stats: List[Dict]) -> None:
        """
        Insert or update civilization meta statistics
        
        Args:
            stats: List of stat dictionaries
        """
        self.client.table('civilization_meta_stats').upsert(stats).execute()
    
    def get_civ_meta_stats(self, 
                          leaderboard: str = 'rm_solo',
                          rank_level: str = 'all') -> List[Dict]:
        """
        Get civilization meta statistics
        
        Args:
            leaderboard: Leaderboard type
            rank_level: Rank level
            
        Returns:
            List of meta stats with civilization names
        """
        response = (self.client.table('civilization_meta_stats')
                   .select('*, civilizations(name)')
                   .eq('leaderboard', leaderboard)
                   .eq('rank_level', rank_level)
                   .order('win_rate', desc=True)
                   .execute())
        return response.data
    
    def get_top_civs_by_winrate(self, 
                                leaderboard: str = 'rm_solo',
                                rank_level: str = 'all',
                                limit: int = 10) -> List[Dict]:
        """Get top civilizations by win rate"""
        response = (self.client.table('civilization_meta_stats')
                   .select('*, civilizations(name)')
                   .eq('leaderboard', leaderboard)
                   .eq('rank_level', rank_level)
                   .order('win_rate', desc=True)
                   .limit(limit)
                   .execute())
        return response.data
    
    # ========================================================================
    # LEADERBOARD
    # ========================================================================
    
    def upsert_leaderboard_players(self, players: List[Dict]) -> None:
        """
        Insert or update leaderboard players
        
        Args:
            players: List of player dictionaries
        """
        self.client.table('leaderboard_players').upsert(players).execute()
    
    def get_leaderboard_players(self, 
                               leaderboard: str = 'rm_solo',
                               limit: int = 50) -> List[Dict]:
        """
        Get leaderboard players
        
        Args:
            leaderboard: Leaderboard type
            limit: Number of players
            
        Returns:
            List of players ordered by rank
        """
        response = (self.client.table('leaderboard_players')
                   .select('*')
                   .eq('leaderboard', leaderboard)
                   .order('rank')
                   .limit(limit)
                   .execute())
        return response.data
    
    # ========================================================================
    # BUILD ORDERS
    # ========================================================================
    
    def create_build_order(self, build_order: Dict) -> Dict:
        """Create a new build order"""
        response = self.client.table('build_orders').insert(build_order).execute()
        return response.data[0] if response.data else None
    
    def get_build_orders_for_civ(self, civ_id: str) -> List[Dict]:
        """Get all build orders for a civilization"""
        response = (self.client.table('build_orders')
                   .select('*')
                   .eq('civ_id', civ_id)
                   .order('created_at', desc=True)
                   .execute())
        return response.data
    
    def get_build_order(self, build_order_id: int) -> Optional[Dict]:
        """Get a specific build order"""
        response = (self.client.table('build_orders')
                   .select('*')
                   .eq('id', build_order_id)
                   .execute())
        return response.data[0] if response.data else None
    
    # ========================================================================
    # STRATEGY ANALYSIS
    # ========================================================================
    
    def create_strategy_analysis(self, analysis: Dict) -> Dict:
        """Create a new strategy analysis"""
        response = self.client.table('strategy_analysis').insert(analysis).execute()
        return response.data[0] if response.data else None
    
    def get_strategy_analyses(self, 
                             civ_id: Optional[str] = None,
                             opponent_civ_id: Optional[str] = None) -> List[Dict]:
        """
        Get strategy analyses
        
        Args:
            civ_id: Filter by civilization
            opponent_civ_id: Filter by opponent civilization
            
        Returns:
            List of strategy analyses
        """
        query = self.client.table('strategy_analysis').select('*')
        
        if civ_id:
            query = query.eq('civ_id', civ_id)
        if opponent_civ_id:
            query = query.eq('opponent_civ_id', opponent_civ_id)
        
        response = query.order('created_at', desc=True).execute()
        return response.data
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def execute_raw_sql(self, query: str) -> Any:
        """
        Execute raw SQL query
        
        Note: Use with caution
        """
        return self.client.rpc('execute_sql', {'query': query}).execute()


# Convenience function
def create_db_client(url: Optional[str] = None, key: Optional[str] = None) -> SupabaseDBClient:
    """Create and return a database client instance"""
    return SupabaseDBClient(url=url, key=key)
