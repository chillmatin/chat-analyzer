"""Conversation pattern analysis for WhatsApp chats."""

from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional
import numpy as np
from analyzers.parser import Message
import config


class PatternAnalyzer:
    """Analyzes conversation patterns in WhatsApp chats."""
    
    def __init__(self, messages: List[Message]):
        """
        Initialize the pattern analyzer.
        
        Args:
            messages: List of parsed messages
        """
        self.messages = messages
    
    def get_response_times(self, participant: str) -> List[float]:
        """
        Get response times for a participant (in minutes).
        Response time is measured from the previous message by another participant.
        
        Args:
            participant: Name of the participant
            
        Returns:
            List of response times in minutes
        """
        response_times = []
        last_message_time = None
        last_sender = None
        
        for msg in self.messages:
            if last_sender and last_sender != msg.sender and msg.sender == participant and last_message_time:
                # This is a response from the participant
                time_diff = (msg.timestamp - last_message_time).total_seconds() / 60
                # Only count reasonable response times
                if time_diff < config.MAX_RESPONSE_TIME_MINUTES:
                    response_times.append(time_diff)
            
            last_message_time = msg.timestamp
            last_sender = msg.sender
        
        return response_times
    
    def get_avg_response_time(self, participant: str) -> Optional[float]:
        """
        Get average response time for a participant in minutes.
        
        Args:
            participant: Name of the participant
            
        Returns:
            Average response time in minutes, or None if no responses
        """
        response_times = self.get_response_times(participant)
        return sum(response_times) / len(response_times) if response_times else None
    
    def get_median_response_time(self, participant: str) -> Optional[float]:
        """
        Get median response time for a participant in minutes.
        
        Args:
            participant: Name of the participant
            
        Returns:
            Median response time in minutes, or None if no responses
        """
        response_times = self.get_response_times(participant)
        return float(np.median(response_times)) if response_times else None
    
    def get_conversation_starters(self) -> Dict[str, int]:
        """
        Get count of conversation starts by each participant.
        A conversation start is defined as a message after a period of silence.
        
        Returns:
            Dictionary mapping participant names to conversation start counts
        """
        starters = defaultdict(int)
        last_message_time = None
        
        for msg in self.messages:
            if last_message_time:
                time_diff = (msg.timestamp - last_message_time).total_seconds() / 3600
                if time_diff > config.CONVERSATION_GAP_HOURS:
                    starters[msg.sender] += 1
            else:
                starters[msg.sender] += 1
            
            last_message_time = msg.timestamp
        
        return dict(starters)
