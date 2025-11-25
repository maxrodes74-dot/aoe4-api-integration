"""
AoE4 World API Client
Comprehensive client for interacting with the AoE4 World API
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import time


class AoE4WorldAPIClient:
    """Client for AoE4 World API"""
    
    BASE_URL = "https://aoe4world.com/api/v0"
    
    def __init__(self, rate_limit_delay: float = 0.5):
        """
        Initialize the API client
        
        Args:
            rate_limit_delay: Delay between requests in seconds (default 0.5)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AoE4-Stats-Integration/1.0'
        })
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Make a request to the API
        
        Args:
            endpoint: API endpoint (e.g., '/stats/rm_solo')
            params: Query parameters
            
        Returns:
            JSON response data
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    # ========================================================================
    # CIVILIZATION STATISTICS
    # ========================================================================
    
    def get_civ_stats(self, leaderboard: str = 'rm_solo', rank_level: str = 'all') -> List[Dict]:
        """
        Get civilization statistics
        
        Args:
            leaderboard: Leaderboard type (rm_solo, rm_team, rm_1v1, rm_2v2, rm_3v3, rm_4v4)
            rank_level: Rank level (all, bronze, silver, gold, platinum, diamond, conqueror)
            
        Returns:
            List of civilization statistics
        """
        endpoint = f"/stats/{leaderboard}"
        params = {'rank_level': rank_level}
        
        data = self._make_request(endpoint, params)
        return data.get('civilizations', [])
    
    def get_all_civ_stats(self) -> List[Dict]:
        """
        Get civilization statistics for all leaderboards and rank levels
        
        Returns:
            List of all civilization statistics
        """
        leaderboards = ['rm_solo', 'rm_team', 'rm_1v1', 'rm_2v2', 'rm_3v3', 'rm_4v4']
        rank_levels = ['all', 'bronze', 'silver', 'gold', 'platinum', 'diamond', 'conqueror']
        
        all_stats = []
        
        for leaderboard in leaderboards:
            for rank_level in rank_levels:
                try:
                    stats = self.get_civ_stats(leaderboard, rank_level)
                    for stat in stats:
                        stat['leaderboard'] = leaderboard
                        stat['rank_level'] = rank_level
                        stat['fetched_at'] = datetime.utcnow().isoformat()
                    all_stats.extend(stats)
                except Exception as e:
                    print(f"Error fetching {leaderboard}/{rank_level}: {e}")
        
        return all_stats
    
    # ========================================================================
    # LEADERBOARD
    # ========================================================================
    
    def get_leaderboard(self, 
                       leaderboard: str = 'rm_solo',
                       count: int = 50,
                       page: int = 1) -> Dict:
        """
        Get leaderboard rankings
        
        Args:
            leaderboard: Leaderboard type
            count: Number of results per page (max 200)
            page: Page number
            
        Returns:
            Leaderboard data with players
        """
        endpoint = f"/leaderboards/{leaderboard}"
        params = {'count': min(count, 200), 'page': page}
        
        return self._make_request(endpoint, params)
    
    def get_top_players(self, leaderboard: str = 'rm_solo', count: int = 50) -> List[Dict]:
        """
        Get top players from leaderboard
        
        Args:
            leaderboard: Leaderboard type
            count: Number of players to fetch
            
        Returns:
            List of player data
        """
        data = self.get_leaderboard(leaderboard, count=count)
        players = data.get('players', [])
        
        # Add metadata
        for player in players:
            player['leaderboard'] = leaderboard
            player['fetched_at'] = datetime.utcnow().isoformat()
        
        return players
    
    # ========================================================================
    # PLAYER DATA
    # ========================================================================
    
    def get_player(self, player_id: int) -> Dict:
        """
        Get player profile
        
        Args:
            player_id: Player ID
            
        Returns:
            Player profile data
        """
        endpoint = f"/players/{player_id}"
        return self._make_request(endpoint)
    
    def search_players(self, query: str) -> List[Dict]:
        """
        Search for players
        
        Args:
            query: Search query (player name)
            
        Returns:
            List of matching players
        """
        endpoint = "/players/search"
        params = {'query': query}
        
        data = self._make_request(endpoint, params)
        return data.get('players', [])
    
    def get_player_games(self, 
                        player_id: int,
                        count: int = 20,
                        page: int = 1) -> List[Dict]:
        """
        Get recent games for a player
        
        Args:
            player_id: Player ID
            count: Number of games per page
            page: Page number
            
        Returns:
            List of game data
        """
        endpoint = f"/players/{player_id}/games"
        params = {'count': count, 'page': page}
        
        data = self._make_request(endpoint, params)
        return data.get('games', [])
    
    # ========================================================================
    # MATCH DATA
    # ========================================================================
    
    def get_game(self, game_id: int) -> Dict:
        """
        Get detailed game/match data
        
        Args:
            game_id: Game ID
            
        Returns:
            Detailed game data
        """
        endpoint = f"/games/{game_id}"
        return self._make_request(endpoint)
    
    # ========================================================================
    # MAP STATISTICS
    # ========================================================================
    
    def get_map_stats(self, leaderboard: str = 'rm_solo') -> List[Dict]:
        """
        Get map statistics
        
        Args:
            leaderboard: Leaderboard type
            
        Returns:
            List of map statistics
        """
        endpoint = f"/stats/{leaderboard}/maps"
        data = self._make_request(endpoint)
        return data.get('maps', [])


# Convenience function
def create_client(rate_limit_delay: float = 0.5) -> AoE4WorldAPIClient:
    """Create and return an API client instance"""
    return AoE4WorldAPIClient(rate_limit_delay=rate_limit_delay)
