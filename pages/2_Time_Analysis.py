"""Time Analysis page - Temporal patterns and activity heatmaps."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui import (
    create_dual_line_chart, create_calendar_heatmap, create_heatmap,
    create_bar_chart, dict_to_dataframe, format_datetime_df,
    add_rolling_average, apply_categorical_order, DAY_ORDER
)

# Check if chat data exists
if 'chat' not in st.session_state:
    st.warning("Please upload a chat file from the Home page first.")
    st.stop()

chat = st.session_state.chat

st.header("Time Analysis")

# Messages over time
st.subheader("Messages Over Time")

# Prepare daily data
messages_by_date = chat.get_messages_by_date()
df_daily = dict_to_dataframe(messages_by_date, 'Date', 'Messages')
df_daily = format_datetime_df(df_daily, 'Date')
df_daily = df_daily.sort_values('Date')

# Add rolling average
df_daily = add_rolling_average(df_daily, 'Messages', window=7)

# Line chart
fig = create_dual_line_chart(
    df_daily, 'Date', 'Messages', '7-day MA',
    'Daily Messages', '7-day Moving Average',
    'Daily Message Count with 7-day Moving Average',
    fill_y1=True
)
st.plotly_chart(fig, width="stretch")

st.divider()

# GitHub-style calendar heatmap
st.subheader("Activity Calendar")

messages_by_date = chat.get_messages_by_date()
df_calendar = dict_to_dataframe(messages_by_date, 'Date', 'Messages')

fig = create_calendar_heatmap(df_calendar, 'Date', 'Messages')
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
pivot = df_heatmap.groupby(['day', 'hour']).size().reset_index(name='count')
pivot_matrix = pivot.pivot(index='day', columns='hour', values='count').fillna(0)
pivot_matrix = pivot_matrix.reindex(DAY_ORDER)

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
    
    fig = create_bar_chart(
        df_hour, 'Hour', 'Messages',
        "Messages by Hour of Day",
        color_scale='messages'
    )
    st.plotly_chart(fig, width="stretch")

with col2:
    day_dist = chat.get_messages_by_day_of_week()
    df_day = dict_to_dataframe(day_dist, 'Day', 'Messages')
    df_day = apply_categorical_order(df_day, 'Day', DAY_ORDER)
    
    fig = create_bar_chart(
        df_day, 'Day', 'Messages',
        "Messages by Day of Week",
        color_scale='activity',
        categorical_order=DAY_ORDER
    )
    st.plotly_chart(fig, width="stretch")

st.divider()

# Weekly trend
st.subheader("Weekly Trend")

messages_by_date = chat.get_messages_by_date()
df_dates = dict_to_dataframe(messages_by_date, 'Date', 'Messages')
df_dates = format_datetime_df(df_dates, 'Date')
df_dates['Week'] = df_dates['Date'].dt.strftime('%Y-W%U')

# Group by week
df_weekly = df_dates.groupby('Week')['Messages'].sum().reset_index()

import plotly.express as px
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
