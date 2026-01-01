import re
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Message:
    """Represents a single WhatsApp message."""
    timestamp: datetime
    sender: str
    content: str
    is_media: bool = False
    media_type: Optional[str] = None  # Sticker, Bild, Standort, etc.
    is_system: bool = False
    has_link: bool = False
    links: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"[{self.timestamp}] {self.sender}: {self.content}"


class WhatsAppChat:
    """
    A comprehensive WhatsApp chat analyzer that extracts all available data from a chat export.
    
    Attributes:
        messages: List of all parsed messages
        participants: Set of all participants in the chat
        message_count: Total number of messages
        media_count: Total number of media messages
        start_date: First message timestamp
        end_date: Last message timestamp
    """
    
    # Regex pattern for WhatsApp messages
    # Format: [DD.MM.YYYY, HH:MM:SS] Sender: Message
    MESSAGE_PATTERN = re.compile(
        r'^\[?(\d{2}\.\d{2}\.\d{4}),\s+(\d{2}:\d{2}:\d{2})\]\s+([^:]+):\s+(.*)$',
        re.MULTILINE
    )
    
    # Media indicators
    MEDIA_INDICATORS = {
        'Bild weggelassen': 'image',
        'Video weggelassen': 'video',
        'Sticker weggelassen': 'sticker',
        'Audio weggelassen': 'audio',
        'Dokument weggelassen': 'document',
        'GIF weggelassen': 'gif',
        'Standort:': 'location',
        '<attached:': 'attachment'
    }
    
    def __init__(self, filepath: str):
        """
        Initialize the WhatsApp chat analyzer.
        
        Args:
            filepath: Path to the WhatsApp chat export file
        """
        self.filepath = filepath
        self.messages: List[Message] = []
        self.participants: set = set()
        
        # Parse the chat file
        self._parse_chat()
        
    def _parse_chat(self):
        """Parse the WhatsApp chat file and extract all messages."""
        with open(self.filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find all messages
        matches = self.MESSAGE_PATTERN.finditer(content)
        
        for match in matches:
            date_str, time_str, sender, message_content = match.groups()
            
            # Parse timestamp
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M:%S")
            
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
            
            # Create message object
            msg = Message(
                timestamp=timestamp,
                sender=sender,
                content=message_content,
                is_media=is_media,
                media_type=media_type,
                is_system=is_system,
                has_link=has_link,
                links=links
            )
            
            self.messages.append(msg)
    
    def _check_media(self, content: str) -> Tuple[bool, Optional[str]]:
        """Check if message contains media and return media type."""
        for indicator, media_type in self.MEDIA_INDICATORS.items():
            if indicator in content:
                return True, media_type
        return False, None
    
    def _is_system_message(self, content: str) -> bool:
        """Check if message is a system message."""
        system_indicators = [
            'Ende-zu-Ende-verschlüsselt',
            'encrypted',
            'added',
            'left',
            'changed',
            'created group'
        ]
        return any(indicator in content for indicator in system_indicators)
    
    def _extract_links(self, content: str) -> List[str]:
        """Extract URLs from message content."""
        url_pattern = re.compile(r'https?://[^\s]+')
        return url_pattern.findall(content)
    
    # ========================
    # Basic Statistics
    # ========================
    
    @property
    def message_count(self) -> int:
        """Total number of messages."""
        return len(self.messages)
    
    @property
    def media_count(self) -> int:
        """Total number of media messages."""
        return sum(1 for msg in self.messages if msg.is_media)
    
    @property
    def start_date(self) -> Optional[datetime]:
        """Timestamp of the first message."""
        return self.messages[0].timestamp if self.messages else None
    
    @property
    def end_date(self) -> Optional[datetime]:
        """Timestamp of the last message."""
        return self.messages[-1].timestamp if self.messages else None
    
    @property
    def duration_days(self) -> int:
        """Duration of the chat in days."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    # ========================
    # Participant Statistics
    # ========================
    
    def get_message_count_by_participant(self) -> Dict[str, int]:
        """Get message count for each participant."""
        counts = Counter(msg.sender for msg in self.messages)
        return dict(counts)
    
    def get_media_count_by_participant(self) -> Dict[str, int]:
        """Get media message count for each participant."""
        counts = Counter(msg.sender for msg in self.messages if msg.is_media)
        return dict(counts)
    
    def get_avg_message_length_by_participant(self) -> Dict[str, float]:
        """Get average message length for each participant."""
        participant_messages = defaultdict(list)
        for msg in self.messages:
            if not msg.is_media and not msg.is_system:
                participant_messages[msg.sender].append(len(msg.content))
        
        return {
            participant: sum(lengths) / len(lengths) if lengths else 0
            for participant, lengths in participant_messages.items()
        }
    
    def get_median_message_length_by_participant(self) -> Dict[str, float]:
        """Get median message length for each participant."""
        import numpy as np
        participant_messages = defaultdict(list)
        for msg in self.messages:
            if not msg.is_media and not msg.is_system:
                participant_messages[msg.sender].append(len(msg.content))
        
        return {
            participant: float(np.median(lengths)) if lengths else 0
            for participant, lengths in participant_messages.items()
        }
    
    def get_most_active_participant(self) -> Optional[str]:
        """Get the participant who sent the most messages."""
        if not self.messages:
            return None
        counts = self.get_message_count_by_participant()
        return max(counts, key=lambda x: counts[x])
    
    # ========================
    # Time-based Statistics
    # ========================
    
    def get_messages_by_hour(self) -> Dict[int, int]:
        """Get message count for each hour of the day (0-23)."""
        counts = Counter(msg.timestamp.hour for msg in self.messages)
        return dict(sorted(counts.items()))
    
    def get_messages_by_day_of_week(self) -> Dict[str, int]:
        """Get message count for each day of the week."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        counts = Counter(days[msg.timestamp.weekday()] for msg in self.messages)
        return dict(counts)
    
    def get_messages_by_month(self) -> Dict[str, int]:
        """Get message count for each month."""
        counts = Counter(msg.timestamp.strftime("%Y-%m") for msg in self.messages)
        return dict(sorted(counts.items()))
    
    def get_messages_by_date(self) -> Dict[str, int]:
        """Get message count for each date."""
        counts = Counter(msg.timestamp.date() for msg in self.messages)
        return {str(date): count for date, count in sorted(counts.items())}
    
    def get_most_active_hour(self) -> Optional[int]:
        """Get the hour with most messages."""
        hour_counts = self.get_messages_by_hour()
        return max(hour_counts, key=lambda x: hour_counts[x]) if hour_counts else None
    
    def get_most_active_day(self) -> Optional[str]:
        """Get the date with most messages."""
        date_counts = self.get_messages_by_date()
        return str(max(date_counts, key=lambda x: date_counts[x])) if date_counts else None
    
    # ========================
    # Content Analysis
    # ========================
    
    def get_media_types(self) -> Dict[str, int]:
        """Get count of each media type."""
        counts = Counter(msg.media_type for msg in self.messages if msg.media_type)
        return dict(counts)
    
    def get_link_count(self) -> int:
        """Get total number of links shared."""
        return sum(len(msg.links) for msg in self.messages)
    
    def get_all_links(self) -> List[str]:
        """Get all links shared in the chat."""
        links = []
        for msg in self.messages:
            links.extend(msg.links)
        return links
    
    def get_links_by_participant(self) -> Dict[str, List[str]]:
        """Get all links shared by each participant."""
        participant_links = defaultdict(list)
        for msg in self.messages:
            if msg.links:
                participant_links[msg.sender].extend(msg.links)
        return dict(participant_links)
    
    def get_word_frequency(self, top_n: int = 50, participant: Optional[str] = None) -> Dict[str, int]:
        """
        Get most frequent words in the chat.
        
        Args:
            top_n: Number of top words to return
            participant: Optional participant name to filter by
        """
        words = []
        for msg in self.messages:
            if not msg.is_media and not msg.is_system:
                if participant is None or msg.sender == participant:
                    # Simple word extraction (can be improved with better tokenization)
                    words.extend(msg.content.lower().split())
        
        # Filter out very short words
        words = [w for w in words if len(w) > 2]
        counts = Counter(words)
        return dict(counts.most_common(top_n))
    
    def get_emoji_frequency(self, top_n: int = 20, participant: Optional[str] = None) -> Dict[str, int]:
        """
        Get most frequent emojis in the chat.
        
        Args:
            top_n: Number of top emojis to return
            participant: Optional participant name to filter by
        """
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+"
        )
        
        emojis = []
        for msg in self.messages:
            if participant is None or msg.sender == participant:
                emojis.extend(emoji_pattern.findall(msg.content))
        
        counts = Counter(emojis)
        return dict(counts.most_common(top_n))
    
    def search_messages(self, keyword: str, case_sensitive: bool = False) -> List[Message]:
        """
        Search for messages containing a specific keyword.
        
        Args:
            keyword: The keyword to search for
            case_sensitive: Whether the search should be case-sensitive
        """
        results = []
        for msg in self.messages:
            content = msg.content if case_sensitive else msg.content.lower()
            search_term = keyword if case_sensitive else keyword.lower()
            if search_term in content:
                results.append(msg)
        return results
    
    def get_messages_by_participant(self, participant: str) -> List[Message]:
        """Get all messages from a specific participant."""
        return [msg for msg in self.messages if msg.sender == participant]
    
    def get_messages_in_date_range(self, start_date: datetime, end_date: datetime) -> List[Message]:
        """Get all messages within a date range."""
        return [msg for msg in self.messages 
                if start_date <= msg.timestamp <= end_date]
    
    # ========================
    # Conversation Patterns
    # ========================
    
    def get_response_times(self, participant: str) -> List[float]:
        """
        Get response times for a participant (in minutes).
        Response time is measured from the previous message by another participant.
        """
        response_times = []
        last_message_time = None
        last_sender = None
        
        for msg in self.messages:
            if last_sender and last_sender != msg.sender and msg.sender == participant and last_message_time:
                # This is a response from the participant
                time_diff = (msg.timestamp - last_message_time).total_seconds() / 60
                # Only count reasonable response times (< 24 hours)
                if time_diff < 1440:
                    response_times.append(time_diff)
            
            last_message_time = msg.timestamp
            last_sender = msg.sender
        
        return response_times
    
    def get_avg_response_time(self, participant: str) -> Optional[float]:
        """Get average response time for a participant in minutes."""
        response_times = self.get_response_times(participant)
        return sum(response_times) / len(response_times) if response_times else None
    
    def get_median_response_time(self, participant: str) -> Optional[float]:
        """Get median response time for a participant in minutes."""
        import numpy as np
        response_times = self.get_response_times(participant)
        return float(np.median(response_times)) if response_times else None
    
    def get_conversation_starters(self) -> Dict[str, int]:
        """
        Get count of conversation starts by each participant.
        A conversation start is defined as a message after > 6 hours of silence.
        """
        starters = defaultdict(int)
        last_message_time = None
        
        for msg in self.messages:
            if last_message_time:
                time_diff = (msg.timestamp - last_message_time).total_seconds() / 3600
                if time_diff > 6:  # More than 6 hours gap
                    starters[msg.sender] += 1
            else:
                starters[msg.sender] += 1
            
            last_message_time = msg.timestamp
        
        return dict(starters)
    
    # ========================
    # Export and Display
    # ========================
    
    def get_summary(self) -> Dict:
        """Get a comprehensive summary of the chat."""
        return {
            'total_messages': self.message_count,
            'total_media': self.media_count,
            'participants': list(self.participants),
            'participant_count': len(self.participants),
            'start_date': self.start_date,
            'end_date': self.end_date,
            'duration_days': self.duration_days,
            'messages_per_participant': self.get_message_count_by_participant(),
            'most_active_participant': self.get_most_active_participant(),
            'most_active_hour': self.get_most_active_hour(),
            'most_active_day': self.get_most_active_day(),
            'total_links': self.get_link_count(),
            'media_types': self.get_media_types(),
        }
    
    def print_summary(self):
        """Print a formatted summary of the chat."""
        summary = self.get_summary()
        
        print("=" * 60)
        print("WhatsApp Chat Analysis Summary")
        print("=" * 60)
        print(f"\nTotal Messages: {summary['total_messages']}")
        print(f"Total Media: {summary['total_media']}")
        print(f"Total Links: {summary['total_links']}")
        print(f"\nParticipants ({summary['participant_count']}): {', '.join(summary['participants'])}")
        print(f"\nChat Duration: {summary['duration_days']} days")
        print(f"From: {summary['start_date']}")
        print(f"To: {summary['end_date']}")
        print(f"\nMost Active Participant: {summary['most_active_participant']}")
        print(f"Most Active Hour: {summary['most_active_hour']}:00")
        
        print("\nMessages per Participant:")
        for participant, count in summary['messages_per_participant'].items():
            percentage = (count / summary['total_messages']) * 100
            print(f"  {participant}: {count} ({percentage:.1f}%)")
        
        if summary['media_types']:
            print("\nMedia Types:")
            for media_type, count in summary['media_types'].items():
                print(f"  {media_type}: {count}")
        
        print("=" * 60)
    
    def __repr__(self):
        return f"WhatsAppChat(messages={self.message_count}, participants={len(self.participants)}, duration={self.duration_days} days)"
    
    def __len__(self):
        return self.message_count


# Example usage
if __name__ == "__main__":
    # Load and analyze the chat
    chat = WhatsAppChat('data/_chat.txt')
    
    # Print summary
    chat.print_summary()
    
    # Additional analysis examples
    print("\n" + "=" * 60)
    print("Additional Analysis")
    print("=" * 60)
    
    # Top 10 most used words
    print("\nTop 10 Most Used Words:")
    for word, count in list(chat.get_word_frequency(10).items())[:10]:
        print(f"  {word}: {count}")
    
    # Top 10 emojis
    print("\nTop 10 Most Used Emojis:")
    for emoji, count in list(chat.get_emoji_frequency(10).items())[:10]:
        print(f"  {emoji}: {count}")
    
    # Message distribution by hour
    print("\nMessages by Hour:")
    hour_dist = chat.get_messages_by_hour()
    for hour in sorted(hour_dist.keys()):
        bar = "█" * (hour_dist[hour] // 100)
        print(f"  {hour:02d}:00 - {hour_dist[hour]:5d} {bar}")
    
    # Average response times
    print("\nAverage Response Times:")
    for participant in chat.participants:
        avg_time = chat.get_avg_response_time(participant)
        if avg_time:
            print(f"  {participant}: {avg_time:.1f} minutes")
