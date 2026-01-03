"""Conversation Patterns page - Response times and conversation starters."""

import streamlit as st
import numpy as np
from ui import create_bar_chart, create_grouped_bar_chart, dict_to_dataframe

# Check if chat data exists
if 'chat' not in st.session_state:
    st.warning("Please upload a chat file from the Home page first.")
    st.stop()

chat = st.session_state.chat

st.header("Conversation Patterns")

# Conversation starters
st.subheader("Conversation Starters")
st.caption("Number of conversations initiated by each participant (after 6+ hours of silence)")

starters = chat.get_conversation_starters()
df_starters = dict_to_dataframe(starters, 'Participant', 'Conversations Started')

col1, col2 = st.columns([2, 1])

with col1:
    fig = create_bar_chart(
        df_starters, 'Participant', 'Conversations Started',
        "Who Starts Conversations?",
        color_scale='Teal'
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
    import pandas as pd
    df_response = pd.DataFrame(response_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_grouped_bar_chart(
            df_response, 'Participant',
            ['Avg Response (min)', 'Median Response (min)'],
            ['Average', 'Median'],
            ['lightblue', 'darkblue'],
            "Average vs Median Response Time"
        )
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.dataframe(df_response, hide_index=True, width="stretch")
