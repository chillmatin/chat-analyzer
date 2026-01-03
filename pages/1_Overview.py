"""Overview page - Chat statistics and participant distribution."""

import streamlit as st
import pandas as pd
from ui import create_pie_chart, dict_to_dataframe, add_percentage_column

# Check if chat data exists
if 'chat' not in st.session_state:
    st.warning("Please upload a chat file from the Home page first.")
    st.stop()

chat = st.session_state.chat

st.header("Chat Overview")

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
    fig = create_pie_chart(
        values=list(msg_counts.values()),
        names=list(msg_counts.keys()),
        title="Message Distribution",
        hole=0.4,
        color_scheme='participants'
    )
    st.plotly_chart(fig, width="stretch")

with col2:
    # Table
    df = dict_to_dataframe(msg_counts, 'Participant', 'Messages', sort_by='Messages', ascending=False)
    df = add_percentage_column(df, 'Messages')
    st.dataframe(df, hide_index=True, width="stretch")
