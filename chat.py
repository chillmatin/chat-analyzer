"""
WhatsApp Chat Analyzer

This module provides a facade for analyzing WhatsApp chat exports.
The actual implementation is delegated to specialized analyzer modules.
"""

from datetime import datetime
from typing import List, Dict, Optional
from analyzers import Message, ChatParser, StatsAnalyzer, PatternAnalyzer


class WhatsAppChat:
    """
    A comprehensive WhatsApp chat analyzer that extracts all available data from a chat export.
    
    This class acts as a facade, delegating to specialized analyzer modules:
    - ChatParser: For parsing messages from chat export files
    - StatsAnalyzer: For statistical analysis (participant, time, content)
    - PatternAnalyzer: For conversation pattern analysis
    
    Attributes:
        messages: List of all parsed messages
        participants: Set of all participants in the chat
        message_count: Total number of messages
        media_count: Total number of media messages
        start_date: First message timestamp
        end_date: Last message timestamp
    """
    
    def __init__(self, filepath: str):
        """
        Initialize the WhatsApp chat analyzer.
        
        Args:
            filepath: Path to the WhatsApp chat export file
        """
        self.filepath = filepath
        
        # Parse the chat file
        parser = ChatParser(filepath)
        self.messages, self.participants = parser.parse()
        
        # Initialize analyzers
        self._stats = StatsAnalyzer(self.messages, self.participants)
        self._patterns = PatternAnalyzer(self.messages)
    
    # ========================
    # Basic Statistics (delegated to StatsAnalyzer)
    # ========================
    
    @property
    def message_count(self) -> int:
        """Total number of messages."""
        return self._stats.message_count
    
    @property
    def media_count(self) -> int:
        """Total number of media messages."""
        return self._stats.media_count
    
    @property
    def start_date(self) -> Optional[datetime]:
        """Timestamp of the first message."""
        return self._stats.start_date
    
    @property
    def end_date(self) -> Optional[datetime]:
        """Timestamp of the last message."""
        return self._stats.end_date
    
    @property
    def duration_days(self) -> int:
        """Duration of the chat in days."""
        return self._stats.duration_days
    
    # ========================
    # Participant Statistics
    # ========================
    
    def get_message_count_by_participant(self) -> Dict[str, int]:
        """Get message count for each participant."""
        return self._stats.get_message_count_by_participant()
    
    def get_media_count_by_participant(self) -> Dict[str, int]:
        """Get media message count for each participant."""
        return self._stats.get_media_count_by_participant()
    
    def get_avg_message_length_by_participant(self) -> Dict[str, float]:
        """Get average message length for each participant."""
        return self._stats.get_avg_message_length_by_participant()
    
    def get_median_message_length_by_participant(self) -> Dict[str, float]:
        """Get median message length for each participant."""
        return self._stats.get_median_message_length_by_participant()
    
    def get_most_active_participant(self) -> Optional[str]:
        """Get the participant who sent the most messages."""
        return self._stats.get_most_active_participant()
    
    # ========================
    # Time-based Statistics
    # ========================
    
    def get_messages_by_hour(self) -> Dict[int, int]:
        """Get message count for each hour of the day (0-23)."""
        return self._stats.get_messages_by_hour()
    
    def get_messages_by_day_of_week(self) -> Dict[str, int]:
        """Get message count for each day of the week."""
        return self._stats.get_messages_by_day_of_week()
    
    def get_messages_by_month(self) -> Dict[str, int]:
        """Get message count for each month."""
        return self._stats.get_messages_by_month()
    
    def get_messages_by_date(self) -> Dict[str, int]:
        """Get message count for each date."""
        return self._stats.get_messages_by_date()
    
    def get_most_active_hour(self) -> Optional[int]:
        """Get the hour with most messages."""
        return self._stats.get_most_active_hour()
    
    def get_most_active_day(self) -> Optional[str]:
        """Get the date with most messages."""
        return self._stats.get_most_active_day()
    
    # ========================
    # Content Analysis
    # ========================
    
    def get_media_types(self) -> Dict[str, int]:
        """Get count of each media type."""
        return self._stats.get_media_types()
    
    def get_link_count(self) -> int:
        """Get total number of links shared."""
        return self._stats.get_link_count()
    
    def get_all_links(self) -> List[str]:
        """Get all links shared in the chat."""
        return self._stats.get_all_links()
    
    def get_links_by_participant(self) -> Dict[str, List[str]]:
        """Get all links shared by each participant."""
        return self._stats.get_links_by_participant()
    
    def get_word_frequency(self, top_n: int = 50, participant: Optional[str] = None) -> Dict[str, int]:
        """
        Get most frequent words in the chat.
        
        Args:
            top_n: Number of top words to return
            participant: Optional participant name to filter by
        """
        return self._stats.get_word_frequency(top_n, participant)
    
    def get_emoji_frequency(self, top_n: int = 20, participant: Optional[str] = None) -> Dict[str, int]:
        """
        Get most frequent emojis in the chat.
        
        Args:
            top_n: Number of top emojis to return
            participant: Optional participant name to filter by
        """
        return self._stats.get_emoji_frequency(top_n, participant)
    
    def search_messages(self, keyword: str, case_sensitive: bool = False) -> List[Message]:
        """
        Search for messages containing a specific keyword.
        
        Args:
            keyword: The keyword to search for
            case_sensitive: Whether the search should be case-sensitive
        """
        return self._stats.search_messages(keyword, case_sensitive)
    
    def get_messages_by_participant(self, participant: str) -> List[Message]:
        """Get all messages from a specific participant."""
        return self._stats.get_messages_by_participant(participant)
    
    def get_messages_in_date_range(self, start_date: datetime, end_date: datetime) -> List[Message]:
        """Get all messages within a date range."""
        return self._stats.get_messages_in_date_range(start_date, end_date)
    
    # ========================
    # Conversation Patterns (delegated to PatternAnalyzer)
    # ========================
    
    def get_response_times(self, participant: str) -> List[float]:
        """
        Get response times for a participant (in minutes).
        Response time is measured from the previous message by another participant.
        """
        return self._patterns.get_response_times(participant)
    
    def get_avg_response_time(self, participant: str) -> Optional[float]:
        """Get average response time for a participant in minutes."""
        return self._patterns.get_avg_response_time(participant)
    
    def get_median_response_time(self, participant: str) -> Optional[float]:
        """Get median response time for a participant in minutes."""
        return self._patterns.get_median_response_time(participant)
    
    def get_conversation_starters(self) -> Dict[str, int]:
        """
        Get count of conversation starts by each participant.
        A conversation start is defined as a message after > 6 hours of silence.
        """
        return self._patterns.get_conversation_starters()
    
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
