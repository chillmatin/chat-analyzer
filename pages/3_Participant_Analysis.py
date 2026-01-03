"""Participant Analysis page - Individual stats and comparisons."""

import streamlit as st
from ui import create_bar_chart, create_area_chart, dict_to_dataframe

# Check if chat data exists
if 'chat' not in st.session_state:
    st.warning("Please upload a chat file from the Home page first.")
    st.stop()

chat = st.session_state.chat

st.header("Participant Analysis")

participants = list(chat.participants)

# Participant selector
selected_participant = st.selectbox("Select Participant", participants)

# Stats for selected participant
col1, col2, col3, col4 = st.columns(4)

msg_counts = chat.get_message_count_by_participant()
media_counts = chat.get_media_count_by_participant()
median_lengths = chat.get_median_message_length_by_participant()

with col1:
    st.metric("Messages Sent", f"{msg_counts.get(selected_participant, 0):,}")
with col2:
    media_count = media_counts.get(selected_participant, 0)
    st.metric("Media Shared", media_count)
with col3:
    median_length = median_lengths.get(selected_participant, 0)
    st.metric("Median Message Length", f"{median_length:.0f} chars")
with col4:
    median_resp = chat.get_median_response_time(selected_participant)
    st.metric("Median Response Time", f"{median_resp:.1f} min" if median_resp else "N/A")

st.divider()

# Comparison charts
st.subheader("Participant Comparison")

col1, col2 = st.columns(2)

with col1:
    # Message count comparison
    df_comp = dict_to_dataframe(msg_counts, 'Participant', 'Messages')
    fig = create_bar_chart(
        df_comp, 'Participant', 'Messages',
        "Total Messages Comparison",
        color_scale='comparison'
    )
    st.plotly_chart(fig, width="stretch")

with col2:
    # Median message length comparison
    df_median = dict_to_dataframe(median_lengths, 'Participant', 'Median Length')
    fig = create_bar_chart(
        df_median, 'Participant', 'Median Length',
        "Median Message Length Comparison",
        color_scale='Plasma'
    )
    st.plotly_chart(fig, width="stretch")

st.divider()

# Activity pattern for selected participant
st.subheader(f"Activity Pattern - {selected_participant}")

participant_messages = chat.get_messages_by_participant(selected_participant)

# Hourly activity
hourly_activity = {}
for msg in participant_messages:
    hour = msg.timestamp.hour
    hourly_activity[hour] = hourly_activity.get(hour, 0) + 1

import pandas as pd
df_hourly = pd.DataFrame({
    'Hour': [f"{h:02d}:00" for h in range(24)],
    'Messages': [hourly_activity.get(h, 0) for h in range(24)]
})

fig = create_area_chart(
    df_hourly, 'Hour', 'Messages',
    f"Hourly Activity - {selected_participant}"
)
st.plotly_chart(fig, width="stretch")
