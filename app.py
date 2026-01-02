import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from chat import WhatsAppChat
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    /* Make file uploader button smaller */
    [data-testid="stFileUploader"] button {
        font-size: 0.85rem !important;
        padding: 0.25rem 0.75rem !important;
    }
    [data-testid="stFileUploader"] {
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Load chat data
@st.cache_data
def load_chat(file_content, filename):
    import tempfile
    import os
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
        tmp_file.write(file_content)
        tmp_path = tmp_file.name
    
    try:
        chat = WhatsAppChat(tmp_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    return chat

# Header
st.markdown('<div class="main-header">💬 WhatsApp Chat Analyzer</div>', unsafe_allow_html=True)

# File uploader in sidebar
with st.sidebar:
    uploaded_file = st.file_uploader(
        "Upload WhatsApp Chat",
        type=['txt'],
        help="Export your WhatsApp chat and upload the .txt file"
    )

# Show instructions if no file uploaded
if uploaded_file is None:
    st.info("👆 Upload your WhatsApp chat export file in the sidebar to begin")
    
    with st.expander("📖 How to export WhatsApp chat"):
        st.markdown("""
        **On Android:**
        1. Open the chat → ⋮ menu → More → Export chat
        2. Choose "Without Media" and save the .txt file
        
        **On iPhone:**
        1. Open the chat → Tap contact name → Export Chat
        2. Choose "Without Media" and save the .txt file
        
        *Your data is processed locally and never stored or transmitted.*
        """)
    st.stop()

# Load the chat
file_content = uploaded_file.read().decode('utf-8')
chat = load_chat(file_content, uploaded_file.name)

# Sidebar
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Select View", [
    "Overview",
    "Time Analysis",
    "Participant Analysis",
    "Content Analysis",
    "Conversation Patterns"
], key="page_selector")

# Track page changes for scrolling
if 'last_page' not in st.session_state:
    st.session_state.last_page = page

page_changed = st.session_state.last_page != page
st.session_state.last_page = page

# Overview metrics
if page == "Overview":
    st.header("📈 Chat Overview")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Messages", f"{chat.message_count:,}")
    with col2:
        st.metric("Duration (Days)", chat.duration_days)
    with col3:
        st.metric("Participants", len(chat.participants))
    with col4:
        st.metric("Media Shared", chat.media_count)
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Links Shared", chat.get_link_count())
    with col6:
        avg_per_day = chat.message_count / max(chat.duration_days, 1)
        st.metric("Avg Messages/Day", f"{avg_per_day:.0f}")
    with col7:
        st.metric("Start Date", chat.start_date.strftime("%Y-%m-%d") if chat.start_date else "N/A")
    with col8:
        st.metric("End Date", chat.end_date.strftime("%Y-%m-%d") if chat.end_date else "N/A")
    
    st.divider()
    
    # Messages per participant
    st.subheader("Messages per Participant")
    msg_counts = chat.get_message_count_by_participant()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pie chart
        fig = px.pie(
            values=list(msg_counts.values()),
            names=list(msg_counts.keys()),
            title="Message Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        # Table
        df = pd.DataFrame({
            'Participant': msg_counts.keys(),
            'Messages': msg_counts.values()
        })
        df['Percentage'] = (df['Messages'] / df['Messages'].sum() * 100).round(1)
        df = df.sort_values('Messages', ascending=False)
        st.dataframe(df, hide_index=True, width="stretch")

# Time Analysis
elif page == "Time Analysis":
    st.header("⏰ Time Analysis")
    
    # Messages over time
    st.subheader("Messages Over Time")
    
    # Prepare daily data
    messages_by_date = chat.get_messages_by_date()
    df_daily = pd.DataFrame({
        'Date': list(messages_by_date.keys()),
        'Messages': list(messages_by_date.values())
    })
    df_daily['Date'] = pd.to_datetime(df_daily['Date'])
    df_daily = df_daily.sort_values('Date')
    
    # Add rolling average
    df_daily['7-day MA'] = df_daily['Messages'].rolling(window=7, center=True).mean()
    
    # Line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_daily['Date'],
        y=df_daily['Messages'],
        mode='lines',
        name='Daily Messages',
        line=dict(color='lightblue', width=1),
        fill='tozeroy',
        fillcolor='rgba(173, 216, 230, 0.3)'
    ))
    fig.add_trace(go.Scatter(
        x=df_daily['Date'],
        y=df_daily['7-day MA'],
        mode='lines',
        name='7-day Moving Average',
        line=dict(color='darkblue', width=3)
    ))
    fig.update_layout(
        title="Daily Message Count with 7-day Moving Average",
        xaxis_title="Date",
        yaxis_title="Number of Messages",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, width="stretch")
    
    st.divider()
    
    # GitHub-style calendar heatmap
    st.subheader("Activity Calendar")
    
    # Prepare calendar data
    messages_by_date = chat.get_messages_by_date()
    df_calendar = pd.DataFrame({
        'Date': list(messages_by_date.keys()),
        'Messages': list(messages_by_date.values())
    })
    df_calendar['Date'] = pd.to_datetime(df_calendar['Date'])
    df_calendar = df_calendar.sort_values('Date')
    
    # Create calendar grid data
    df_calendar['Week'] = df_calendar['Date'].dt.isocalendar().week
    df_calendar['Year'] = df_calendar['Date'].dt.year
    df_calendar['Weekday'] = df_calendar['Date'].dt.dayofweek
    df_calendar['YearWeek'] = df_calendar['Year'].astype(str) + '-W' + df_calendar['Week'].astype(str).str.zfill(2)
    
    # Create pivot for heatmap
    calendar_pivot = df_calendar.pivot_table(
        index='Weekday',
        columns='YearWeek',
        values='Messages',
        fill_value=0
    )
    
    # Create custom hover text
    hover_text = []
    for weekday in range(7):
        row_text = []
        for yearweek in calendar_pivot.columns:
            matching_dates = df_calendar[
                (df_calendar['YearWeek'] == yearweek) & 
                (df_calendar['Weekday'] == weekday)
            ]
            if not matching_dates.empty:
                date = matching_dates.iloc[0]['Date'].strftime('%Y-%m-%d')
                count = int(matching_dates.iloc[0]['Messages'])
                row_text.append(f"{date}<br>{count} messages")
            else:
                row_text.append("")
        hover_text.append(row_text)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=calendar_pivot.values,
        x=calendar_pivot.columns,
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        colorscale=[
            [0, '#ebedf0'],
            [0.2, '#9be9a8'],
            [0.4, '#40c463'],
            [0.6, '#30a14e'],
            [0.8, '#216e39'],
            [1, '#0d4429']
        ],
        hovertemplate='%{hovertext}<extra></extra>',
        hovertext=hover_text,
        showscale=True,
        colorbar=dict(title="Messages")
    ))
    
    fig.update_layout(
        title="Daily Activity Calendar",
        xaxis_title="Week",
        yaxis_title="Day of Week",
        height=300,
        xaxis=dict(
            tickangle=-45,
            tickmode='linear',
            tick0=0,
            dtick=max(1, len(calendar_pivot.columns) // 20)  # Show fewer ticks if many weeks
        ),
        yaxis=dict(autorange='reversed')
    )
    st.plotly_chart(fig, width="stretch")
    
    st.divider()
    
    # Daily Heatmap
    st.subheader("Daily Activity Heatmap")
    
    # Prepare heatmap data
    heatmap_data = []
    for msg in chat.messages:
        heatmap_data.append({
            'hour': msg.timestamp.hour,
            'day': msg.timestamp.strftime('%A'),
            'day_num': msg.timestamp.weekday()
        })
    
    df_heatmap = pd.DataFrame(heatmap_data)
    
    # Create pivot table
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = df_heatmap.groupby(['day', 'hour']).size().reset_index(name='count')
    pivot_matrix = pivot.pivot(index='day', columns='hour', values='count').fillna(0)
    pivot_matrix = pivot_matrix.reindex(days_order)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_matrix.values,
        x=[f"{h:02d}:00" for h in range(24)],
        y=pivot_matrix.index,
        colorscale='YlOrRd',
        text=pivot_matrix.values,
        texttemplate='%{text:.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Messages")
    ))
    fig.update_layout(
        title="Messages by Day of Week and Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=500
    )
    st.plotly_chart(fig, width="stretch")
    
    st.divider()
    
    # Hourly distribution
    st.subheader("Hourly Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hour_dist = chat.get_messages_by_hour()
        df_hour = pd.DataFrame({
            'Hour': [f"{h:02d}:00" for h in hour_dist.keys()],
            'Messages': list(hour_dist.values())
        })
        
        fig = px.bar(
            df_hour,
            x='Hour',
            y='Messages',
            title="Messages by Hour of Day",
            color='Messages',
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        day_dist = chat.get_messages_by_day_of_week()
        df_day = pd.DataFrame({
            'Day': list(day_dist.keys()),
            'Messages': list(day_dist.values())
        })
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_day['Day'] = pd.Categorical(df_day['Day'], categories=day_order, ordered=True)
        df_day = df_day.sort_values('Day')
        
        fig = px.bar(
            df_day,
            x='Day',
            y='Messages',
            title="Messages by Day of Week",
            color='Messages',
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, width="stretch")
    
    st.divider()
    
    # Weekly trend
    st.subheader("Weekly Trend")
    messages_by_date = chat.get_messages_by_date()
    df_dates = pd.DataFrame({
        'Date': list(messages_by_date.keys()),
        'Messages': list(messages_by_date.values())
    })
    df_dates['Date'] = pd.to_datetime(df_dates['Date'])
    df_dates['Week'] = df_dates['Date'].dt.strftime('%Y-W%U')
    
    # Group by week
    df_weekly = df_dates.groupby('Week')['Messages'].sum().reset_index()
    
    fig = px.line(
        df_weekly,
        x='Week',
        y='Messages',
        title="Messages by Week",
        markers=True
    )
    fig.update_traces(line_color='#ff6b6b', line_width=3, marker=dict(size=8))
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, width="stretch")

# Participant Analysis
elif page == "Participant Analysis":
    st.header("👥 Participant Analysis")
    
    participants = list(chat.participants)
    
    # Participant selector
    selected_participant = st.selectbox("Select Participant", participants)
    
    # Stats for selected participant
    col1, col2, col3, col4 = st.columns(4)
    
    msg_counts = chat.get_message_count_by_participant()
    if msg_counts is None:
        msg_counts = {}
    media_counts = chat.get_media_count_by_participant()
    if media_counts is None:
        media_counts = {}
    median_lengths = chat.get_median_message_length_by_participant()
    if median_lengths is None:
        median_lengths = {}
    
    with col1:
        st.metric("Messages Sent", f"{msg_counts.get(selected_participant, 0) if selected_participant else 0:,}")
    with col2:
        media_count = media_counts.get(selected_participant, 0) if media_counts and selected_participant else 0
        st.metric("Media Shared", media_count)
    with col3:
        median_length = median_lengths.get(selected_participant, 0) if median_lengths and selected_participant else 0
        st.metric("Median Message Length", f"{median_length:.0f} chars")
    with col4:
        median_resp = chat.get_median_response_time(selected_participant) if selected_participant else None
        st.metric("Median Response Time", f"{median_resp:.1f} min" if median_resp else "N/A")
    
    st.divider()
    
    # Comparison charts
    st.subheader("Participant Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Message count comparison
        df_comp = pd.DataFrame({
            'Participant': list(msg_counts.keys()),
            'Messages': list(msg_counts.values())
        })
        fig = px.bar(
            df_comp,
            x='Participant',
            y='Messages',
            title="Total Messages Comparison",
            color='Messages',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        # Median message length comparison
        df_median = pd.DataFrame({
            'Participant': list(median_lengths.keys()),
            'Median Length': list(median_lengths.values())
        })
        fig = px.bar(
            df_median,
            x='Participant',
            y='Median Length',
            title="Median Message Length Comparison",
            color='Median Length',
            color_continuous_scale='Plasma'
        )
        st.plotly_chart(fig, width="stretch")
    
    st.divider()
    
    # Activity pattern for selected participant
    st.subheader(f"Activity Pattern - {selected_participant}")
    
    participant_messages = chat.get_messages_by_participant(selected_participant) if selected_participant else []
    
    # Hourly activity
    hourly_activity = {}
    for msg in participant_messages:
        hour = msg.timestamp.hour
        hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
    
    df_hourly = pd.DataFrame({
        'Hour': [f"{h:02d}:00" for h in range(24)],
        'Messages': [hourly_activity.get(h, 0) for h in range(24)]
    })
    
    fig = px.area(
        df_hourly,
        x='Hour',
        y='Messages',
        title=f"Hourly Activity - {selected_participant}",
        color_discrete_sequence=['#636EFA']
    )
    fig.update_traces(fill='tozeroy')
    st.plotly_chart(fig, width="stretch")

# Content Analysis
elif page == "Content Analysis":
    st.header("📝 Content Analysis")
    
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
        import os
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
            'collocations': False  # Avoid word pairs
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
    df_words = pd.DataFrame({
        'Word': list(word_freq.keys()),
        'Count': list(word_freq.values())
    })
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            df_words.head(20),
            x='Count',
            y='Word',
            orientation='h',
            title="Top 20 Most Used Words",
            color='Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.dataframe(df_words.head(20), hide_index=True, width="stretch", height=600)
    
    st.divider()
    
    # Emojis
    st.subheader("Most Frequent Emojis" + (f" - {selected_participant}" if filter_participant else ""))
    
    emoji_freq = chat.get_emoji_frequency(30, participant=filter_participant)
    
    if emoji_freq:
        df_emoji = pd.DataFrame({
            'Emoji': list(emoji_freq.keys()),
            'Count': list(emoji_freq.values())
        })
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                df_emoji.head(20),
                x='Count',
                y='Emoji',
                orientation='h',
                title="Top 20 Most Used Emojis",
                color='Count',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.dataframe(df_emoji.head(20), hide_index=True, width="stretch", height=600)
    else:
        st.info("No emojis found in the chat.")
    
    st.divider()
    
    # Media analysis
    st.subheader("Media Shared")
    
    media_types = chat.get_media_types()
    
    if media_types:
        col1, col2 = st.columns(2)
        
        with col1:
            df_media = pd.DataFrame({
                'Type': list(media_types.keys()),
                'Count': list(media_types.values())
            })
            
            fig = px.pie(
                df_media,
                values='Count',
                names='Type',
                title="Media Types Distribution",
                color_discrete_sequence=px.colors.sequential.Sunset
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

# Conversation Patterns
elif page == "Conversation Patterns":
    st.header("🔄 Conversation Patterns")
    
    # Conversation starters
    st.subheader("Conversation Starters")
    st.caption("Number of conversations initiated by each participant (after 6+ hours of silence)")
    
    starters = chat.get_conversation_starters()
    df_starters = pd.DataFrame({
        'Participant': list(starters.keys()),
        'Conversations Started': list(starters.values())
    })
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            df_starters,
            x='Participant',
            y='Conversations Started',
            title="Who Starts Conversations?",
            color='Conversations Started',
            color_continuous_scale='Teal'
        )
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.dataframe(df_starters, hide_index=True, width="stretch")
    
    st.divider()
    
    # Response time analysis
    st.subheader("Response Time Analysis")
    
    response_data = []
    for participant in chat.participants:
        response_times = chat.get_response_times(participant)
        if response_times:
            response_data.append({
                'Participant': participant,
                'Avg Response (min)': np.mean(response_times),
                'Median Response (min)': np.median(response_times),
                'Min Response (min)': np.min(response_times),
                'Max Response (min)': np.max(response_times)
            })
    
    if response_data:
        df_response = pd.DataFrame(response_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_response['Participant'],
                y=df_response['Avg Response (min)'],
                name='Average',
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                x=df_response['Participant'],
                y=df_response['Median Response (min)'],
                name='Median',
                marker_color='darkblue'
            ))
            fig.update_layout(
                title="Average vs Median Response Time",
                yaxis_title="Minutes",
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.dataframe(df_response, hide_index=True, width="stretch")

# Footer
st.sidebar.divider()
start_date_str = chat.start_date.strftime('%Y-%m-%d') if chat.start_date else 'N/A'
end_date_str = chat.end_date.strftime('%Y-%m-%d') if chat.end_date else 'N/A'
st.sidebar.info(f"""
**Chat Statistics**
- Total Messages: {chat.message_count:,}
- Duration: {chat.duration_days} days
- Period: {start_date_str} to {end_date_str}
""")

# Scroll to top after content is rendered (only when page changes)
if page_changed:
    st.markdown("""
        <script>
            setTimeout(function() {
                window.parent.document.querySelector('.main').scrollTop = 0;
            }, 100);
        </script>
    """, unsafe_allow_html=True)
