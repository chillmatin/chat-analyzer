"""Content Analysis page - Words, emojis, media, and message search."""

import streamlit as st
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from ui import create_horizontal_bar_chart, create_pie_chart, dict_to_dataframe

# Check if chat data exists
if 'chat' not in st.session_state:
    st.warning("Please upload a chat file from the Home page first.")
    st.stop()

chat = st.session_state.chat

st.header("Content Analysis")

# Participant filter
participants_list = ['All Participants'] + list(chat.participants)
selected_participant = st.selectbox("Filter by Participant", participants_list)

filter_participant = None if selected_participant == 'All Participants' else selected_participant

# Word Cloud
st.subheader("Word Cloud" + (f" - {selected_participant}" if filter_participant else ""))

# Generate word cloud
word_freq = chat.get_word_frequency(200, participant=filter_participant)

if word_freq:
    # Try to find a unicode-compatible font
    font_path = None
    
    # Common unicode font paths on different systems
    possible_fonts = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',  # macOS
        'C:\\Windows\\Fonts\\Arial.ttf',  # Windows
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',  # Linux alternative
        '/usr/share/fonts/google-noto/NotoSans-Regular.ttf',  # Noto Sans
    ]
    
    for font in possible_fonts:
        if os.path.exists(font):
            font_path = font
            break
    
    # Generate word cloud with unicode support
    wordcloud_params = {
        'width': 1200,
        'height': 600,
        'background_color': 'white',
        'colormap': 'viridis',
        'relative_scaling': 0.5,
        'min_font_size': 10,
        'max_words': 200,
        'collocations': False
    }
    
    if font_path:
        wordcloud_params['font_path'] = font_path
    
    wordcloud = WordCloud(**wordcloud_params).generate_from_frequencies(word_freq)
    
    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout(pad=0)
    st.pyplot(fig)
    plt.close()
else:
    st.info("No words available for word cloud")

st.divider()

# Top words
st.subheader("Most Frequent Words" + (f" - {selected_participant}" if filter_participant else ""))

word_freq = chat.get_word_frequency(50, participant=filter_participant)
df_words = dict_to_dataframe(word_freq, 'Word', 'Count')

col1, col2 = st.columns([2, 1])

with col1:
    # Sort ascending for horizontal bar (first row shows at bottom, so lowest count at bottom)
    df_words_sorted = df_words.head(20).sort_values('Count', ascending=True)
    fig = create_horizontal_bar_chart(
        df_words_sorted, 'Count', 'Word',
        "Top 20 Most Used Words",
        color_scale='words'
    )
    st.plotly_chart(fig, width="stretch")

with col2:
    st.dataframe(df_words.head(20), hide_index=True, width="stretch", height=600)

st.divider()

# Media analysis
st.subheader("Media Shared")

media_types = chat.get_media_types()

if media_types:
    col1, col2 = st.columns(2)
    
    with col1:
        df_media = dict_to_dataframe(media_types, 'Type', 'Count')
        
        fig = create_pie_chart(
            values=df_media['Count'].tolist(),
            names=df_media['Type'].tolist(),
            title="Media Types Distribution",
            color_scheme='media'
        )
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.dataframe(df_media, hide_index=True, width="stretch")
        st.metric("Total Links Shared", chat.get_link_count())
else:
    st.info("No media shared in the chat.")

st.divider()

# Search functionality
st.subheader("Search Messages")
search_term = st.text_input("Enter search term")

if search_term:
    results = chat.search_messages(search_term, case_sensitive=False)
    st.write(f"Found {len(results)} messages containing '{search_term}'")
    
    if results:
        # Show first 50 results
        for i, msg in enumerate(results[:50]):
            with st.expander(f"{msg.timestamp.strftime('%Y-%m-%d %H:%M')} - {msg.sender}"):
                st.write(msg.content)
        
        if len(results) > 50:
            st.info(f"Showing first 50 of {len(results)} results")
