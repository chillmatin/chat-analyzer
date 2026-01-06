"""Location data analysis for WhatsApp chats."""

from typing import List, Dict, Optional, Tuple
from .parser import Message


class LocationAnalyzer:
    """Analyzes location data shared in WhatsApp chats."""
    
    def __init__(self, messages: List[Message]):
        """
        Initialize the location analyzer.
        
        Args:
            messages: List of parsed messages
        """
        self.messages = messages
    
    def get_all_locations(self) -> List[dict]:
        """
        Get all location data from messages.
        
        Returns:
            List of location dictionaries with latitude, longitude, source, link, place, sender, timestamp
        """
        locations = []
        for msg in self.messages:
            if msg.location_data:
                location = msg.location_data.copy()
                location['sender'] = msg.sender
                location['timestamp'] = msg.timestamp
                location['content'] = msg.content
                locations.append(location)
        return locations
    
    def get_locations_by_participant(self) -> Dict[str, List[dict]]:
        """
        Get locations grouped by participant.
        
        Returns:
            Dictionary mapping participant names to their location lists
        """
        participant_locations = {}
        for msg in self.messages:
            if msg.location_data:
                if msg.sender not in participant_locations:
                    participant_locations[msg.sender] = []
                location = msg.location_data.copy()
                location['timestamp'] = msg.timestamp
                location['content'] = msg.content
                participant_locations[msg.sender].append(location)
        return participant_locations
    
    def get_location_count(self) -> int:
        """
        Get total number of locations shared.
        
        Returns:
            Total count of location messages
        """
        return sum(1 for msg in self.messages if msg.location_data)
    
    def get_location_count_by_participant(self) -> Dict[str, int]:
        """
        Get location count for each participant.
        
        Returns:
            Dictionary mapping participant names to location counts
        """
        counts = {}
        for msg in self.messages:
            if msg.location_data:
                counts[msg.sender] = counts.get(msg.sender, 0) + 1
        return counts
    
    def get_location_count_by_source(self) -> Dict[str, int]:
        """
        Get location count by source (Google Maps, Apple Maps, Foursquare).
        
        Returns:
            Dictionary mapping source names to counts
        """
        counts = {}
        for msg in self.messages:
            if msg.location_data:
                source = msg.location_data.get('source', 'Unknown')
                counts[source] = counts.get(source, 0) + 1
        return counts
    
    def get_location_bounds(self) -> Optional[Dict[str, float]]:
        """
        Get the bounding box for all locations with coordinates.
        
        Returns:
            Dictionary with min_lat, max_lat, min_lon, max_lon, or None if no locations
        """
        lats = []
        lons = []
        
        for msg in self.messages:
            if msg.location_data:
                lat = msg.location_data.get('latitude')
                lon = msg.location_data.get('longitude')
                if lat is not None and lon is not None:
                    lats.append(lat)
                    lons.append(lon)
        
        if not lats or not lons:
            return None
        
        return {
            'min_lat': min(lats),
            'max_lat': max(lats),
            'min_lon': min(lons),
            'max_lon': max(lons),
            'center_lat': (min(lats) + max(lats)) / 2,
            'center_lon': (min(lons) + max(lons)) / 2
        }
    
    def get_locations_with_coords(self) -> List[dict]:
        """
        Get only locations that have valid coordinates.
        
        Returns:
            List of location dictionaries with non-null latitude and longitude
        """
        locations = []
        for msg in self.messages:
            if msg.location_data:
                lat = msg.location_data.get('latitude')
                lon = msg.location_data.get('longitude')
                if lat is not None and lon is not None:
                    location = msg.location_data.copy()
                    location['sender'] = msg.sender
                    location['timestamp'] = msg.timestamp
                    location['content'] = msg.content
                    locations.append(location)
        return locations
