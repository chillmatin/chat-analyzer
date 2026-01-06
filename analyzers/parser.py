"""WhatsApp message parser."""

import re
from datetime import datetime
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
import config


@dataclass
class Message:
    """Represents a single WhatsApp message."""
    timestamp: datetime
    sender: str
    content: str
    is_media: bool = False
    media_type: Optional[str] = None  
    is_system: bool = False
    has_link: bool = False
    links: List[str] = field(default_factory=list)
    location_data: Optional[dict] = None  # {latitude, longitude, source, link, place}
    attachment_name: Optional[str] = None  # Filename for attachments
    
    def __str__(self):
        return f"[{self.timestamp}] {self.sender}: {self.content}"


class ChatParser:
    """Parses WhatsApp chat export files."""
    
    def __init__(self, filepath: str):
        """
        Initialize the parser.
        
        Args:
            filepath: Path to the WhatsApp chat export file
        """
        self.filepath = filepath
        self.messages: List[Message] = []
        self.participants: set = set()
        
    def parse(self) -> Tuple[List[Message], set]:
        """
        Parse the chat file and return messages and participants.
        
        Returns:
            Tuple of (messages list, participants set)
        """
        with open(self.filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Remove invisible Unicode characters that might interfere with parsing
        for char in ('\u200e', '\ufeff', '\u202a', '\u202c'):
            content = content.replace(char, '')
        
        # Try multiple patterns for different WhatsApp export formats
        patterns = [
            # Format 1: M/D/YY, HH:MM - Name: message (Android English)
            re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2})\s+-\s+([^:]+?):\s+(.*)$', re.MULTILINE),
            # Format 2: [DD.MM.YY, HH:MM:SS] Name: message (iOS/Android non-English)
            re.compile(r'^\[?(\d{2}\.\d{2}\.\d{2,4}),\s+(\d{1,2}:\d{2}:\d{2})\]\s+([^:]+?):\s+(.*)$', re.MULTILINE),
        ]
        
        best_matches = []
        best_pattern_idx = 0
        
        # Find which pattern works best
        for idx, pattern in enumerate(patterns):
            matches = list(pattern.finditer(content))
            if len(matches) > len(best_matches):
                best_matches = matches
                best_pattern_idx = idx
        
        if not best_matches:
            return self.messages, self.participants
        
        for match in best_matches:
            if best_pattern_idx == 0:
                # Android English format: M/D/YY, HH:MM - Name: message
                timestamp = self._parse_android_date(match.groups())
            elif best_pattern_idx == 1:
                # iOS format: [DD.MM.YY, HH:MM:SS] Name: message
                timestamp = self._parse_ios_date(match.groups())
            else:
                continue
            
            if timestamp is None:
                continue
            
            date_str, time_str, sender, message_content = match.groups()
            
            # Clean sender name
            sender = sender.strip()
            self.participants.add(sender)
            
            # Clean message content
            message_content = message_content.strip()
            
            # Check if it's a media message
            is_media, media_type = self._check_media(message_content)
            
            # Check if it's a system message
            is_system = self._is_system_message(message_content)
            
            # Extract links
            links = self._extract_links(message_content)
            has_link = len(links) > 0
            
            # Extract location data
            location_data = self._extract_location(message_content)
            
            # Extract attachment info
            attachment_name = self._extract_attachment_info(message_content)
            
            # Create message object
            msg = Message(
                timestamp=timestamp,
                sender=sender,
                content=message_content,
                is_media=is_media,
                media_type=media_type,
                is_system=is_system,
                has_link=has_link,
                links=links,
                location_data=location_data,
                attachment_name=attachment_name
            )
            
            self.messages.append(msg)
        
        return self.messages, self.participants
    
    def _parse_android_date(self, groups: tuple) -> Optional[datetime]:
        """Parse Android format date."""
        date_str, time_str, _, _ = groups
        
        for fmt in config.DATE_FORMATS_ANDROID:
            try:
                return datetime.strptime(f"{date_str} {time_str}", fmt)
            except ValueError:
                continue
        return None
    
    def _parse_ios_date(self, groups: tuple) -> Optional[datetime]:
        """Parse iOS format date."""
        date_str, time_str, _, _ = groups
        
        for fmt in config.DATE_FORMATS_IOS:
            try:
                return datetime.strptime(f"{date_str} {time_str}", fmt)
            except ValueError:
                continue
        return None
    
    def _check_media(self, content: str) -> Tuple[bool, Optional[str]]:
        """Check if message contains media and return media type."""
        for indicator, media_type in config.MEDIA_INDICATORS.items():
            if indicator in content:
                return True, media_type
        return False, None
    
    def _is_system_message(self, content: str) -> bool:
        """Check if message is a system message."""
        return any(indicator in content.lower() for indicator in config.SYSTEM_MESSAGE_INDICATORS)
    
    def _extract_links(self, content: str) -> List[str]:
        """Extract URLs from message content."""
        url_pattern = re.compile(r'https?://[^\s]+')
        return url_pattern.findall(content)
    
    def _extract_location(self, content: str) -> Optional[dict]:
        """Extract location data from Google Maps, Apple Maps, or Foursquare links."""
        # Google Maps pattern: https://maps.google.com/?q=latitude,longitude
        google_pattern = re.compile(
            r'https://maps\.google\.com/\?q=(?P<latitude>-?[0-9\.]+),(?P<longitude>-?[0-9\.]+)',
            re.IGNORECASE
        )
        google_match = google_pattern.search(content)
        if google_match:
            return {
                'latitude': float(google_match.group('latitude')),
                'longitude': float(google_match.group('longitude')),
                'source': 'Google Maps',
                'link': google_match.group(0),
                'place': None
            }
        
        # Foursquare pattern: Place name: https://foursquare.com/...
        foursquare_pattern = re.compile(
            r'^(?P<place>.*?):\s*(?P<link>https://foursquare\.com[^\s]+)',
            re.IGNORECASE | re.MULTILINE
        )
        foursquare_match = foursquare_pattern.search(content)
        if foursquare_match:
            return {
                'latitude': None,  # Foursquare doesn't expose coords in link
                'longitude': None,
                'source': 'Foursquare',
                'link': foursquare_match.group('link'),
                'place': foursquare_match.group('place').strip()
            }
        
        # Apple Maps pattern: https://maps.apple.com/?...
        apple_pattern = re.compile(
            r'https://maps\.apple\.com/\?[^\s]*(?:ll=(?P<latitude>-?[0-9\.]+),(?P<longitude>-?[0-9\.]+))?',
            re.IGNORECASE
        )
        apple_match = apple_pattern.search(content)
        if apple_match:
            lat = apple_match.group('latitude')
            lon = apple_match.group('longitude')
            return {
                'latitude': float(lat) if lat else None,
                'longitude': float(lon) if lon else None,
                'source': 'Apple Maps',
                'link': apple_match.group(0),
                'place': None
            }
        
        return None
    
    def _extract_attachment_info(self, content: str) -> Optional[str]:
        """Extract attachment filename from iOS/Android patterns."""
        # iOS pattern: <attached: filename>
        ios_pattern = re.compile(r'<attached:\s*(?P<filename>[^>]+)>', re.IGNORECASE)
        ios_match = ios_pattern.search(content)
        if ios_match:
            return ios_match.group('filename').strip()
        
        # Android pattern: filename (file attached)
        android_pattern = re.compile(r'^(?P<filename>.+?)\s*\(file attached\)', re.IGNORECASE)
        android_match = android_pattern.search(content)
        if android_match:
            return android_match.group('filename').strip()
        
        return None
