"""Configuration constants for WhatsApp Chat Analyzer."""

# Media indicators (multi-language support)
MEDIA_INDICATORS = {
    # German
    'Bild weggelassen': 'image',
    'Video weggelassen': 'video',
    'Sticker weggelassen': 'sticker',
    'Audio weggelassen': 'audio',
    'Dokument weggelassen': 'document',
    'GIF weggelassen': 'gif',
    'Standort:': 'location',
    # English
    'image omitted': 'image',
    'video omitted': 'video',
    'sticker omitted': 'sticker',
    'audio omitted': 'audio',
    'document omitted': 'document',
    'GIF omitted': 'gif',
    'Location:': 'location',
    # Android English generic
    '<Media omitted>': 'media',
    # Generic
    '<attached:': 'attachment'
}

# System message indicators
SYSTEM_MESSAGE_INDICATORS = [
    'Ende-zu-Ende-verschlüsselt',
    'end-to-end encrypted',
    'encrypted',
    'added',
    'left',
    'changed',
    'created group',
    'changed their phone number',
    'security code changed'
]

# Conversation patterns
CONVERSATION_GAP_HOURS = 6  # Hours of silence before considering a new conversation
MAX_RESPONSE_TIME_MINUTES = 1440  # 24 hours

# Content analysis
MIN_WORD_LENGTH = 2  # Minimum word length for word frequency analysis

# Date formats to try when parsing messages
DATE_FORMATS_ANDROID = [
    "%m/%d/%y %H:%M",
    "%m/%d/%Y %H:%M",
    "%d/%m/%y %H:%M",
    "%d/%m/%Y %H:%M",
]

DATE_FORMATS_IOS = [
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%y %H:%M:%S",
]
